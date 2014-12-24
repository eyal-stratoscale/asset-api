import zmq
from asset import api
import threading
from asset.tcp import allocation
from asset.tcp import heartbeat
from asset.tcp import suicide
from asset.tcp import config


class Client(api.Client):
    def __init__(self, providerLocation):
        self._providerLocation = providerLocation
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        self._socket.connect(providerLocation)
        self._socket.setsockopt(zmq.LINGER, 0)
        self._lock = threading.Lock()
        self._closed = False
        self._activeAllocations = []
        self.call("handshake", versionInfo=dict(
            ASSET_VERSION=api.VERSION,
            ZERO_MQ=dict(
                PYZMQ_VERSION=zmq.pyzmq_version(),
                VERSION=zmq.VERSION,
                VERSION_MAJOR=zmq.VERSION_MAJOR,
                VERSION_MINOR=zmq.VERSION_MINOR,
                VERSION_PATCH=zmq.VERSION_PATCH)))
        self._connectionToProviderInterrupted = suicide.killSelf
        self._heartbeat = heartbeat.HeartBeat(self)

    def allocate(self, assetKind, assetCount=1, pool=None, continent=None, allocationInfo=None):
        assert assetCount > 0
        if continent is None:
            continent = config.config.defaultContinent()
        if allocationInfo is None:
            allocationInfo = api.AllocationInfo(
                config.config.defaultUser(), config.config.defaultPurpose())
        allocationID = self.call(
            cmd='allocate',
            assetKind=assetKind,
            assetCount=assetCount,
            pool=pool,
            continent=continent,
            allocationInfo=allocationInfo.__dict__)
        allocationInstance = allocation.Allocation(
            id=allocationID, ipcClient=self, heartbeat=self._heartbeat, assetKind=assetKind)
        self._activeAllocations.append(allocationInstance)
        return allocationInstance

    def call(self, cmd, ipcTimeoutMS=3000, ** kwargs):
        with self._lock:
            if self._closed:
                raise Exception("Already closed")
            return self._call(cmd, ipcTimeoutMS, kwargs)

    def _call(self, cmd, ipcTimeoutMS, arguments):
        self._socket.send_json(dict(cmd=cmd, arguments=arguments))
        hasData = self._socket.poll(ipcTimeoutMS)
        if not hasData:
            self._closeLocked()
            raise Exception("IPC command '%s' timed out" % cmd)
        result = self._socket.recv_json(zmq.NOBLOCK)
        if isinstance(result, dict) and 'exceptionType' in result:
            if result['exceptionType'] == 'NotEnoughResourcesForAllocation':
                raise api.NotEnoughResourcesForAllocation(result['exceptionString'])
            else:
                raise Exception("IPC command '%s' failed: %s: '%s'" % (
                    cmd, result['exceptionType'], result['exceptionString']))
        return result

    def close(self):
        with self._lock:
            assert len(self._activeAllocations) == 0
            self._closeLocked()

    def _closeLocked(self):
        if self._closed:
            return
        self._closed = True
        self._heartbeat.stop()
        self._socket.close()
        self._context.destroy()

    def heartbeatFailed(self):
        self._notifyAllActiveAllocationsThatConnectionToProviderInterrupted()
        self.close()
        self._connectionToProviderInterrupted()

    def _notifyAllActiveAllocationsThatConnectionToProviderInterrupted(self):
        for allocationInstance in list(self._activeAllocations):
            allocationInstance.connectionToProviderInterrupted()
        assert len(self._activeAllocations) == 0

    def setConnectionToProviderInterruptedCallback(self, callback):
        self._connectionToProviderInterrupted = callback

    def allocationClosed(self, allocationInstance):
        self._activeAllocations.remove(allocationInstance)
