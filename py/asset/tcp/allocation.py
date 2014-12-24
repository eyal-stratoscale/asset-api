from asset import api
import logging


class Allocation(api.Allocation):
    def __init__(self, id, ipcClient, heartbeat, assetKind):
        self._id = id
        self._ipcClient = ipcClient
        self._heartbeat = heartbeat
        self._assetKind = assetKind
        self._forceReleaseCallback = None
        self._heartbeat.register(id)
        logging.info("allocation created")

    def assets(self):
        assert self._id is not None
        return self._ipcClient.call('allocation__assets', id=self._id)

    def pool(self):
        assert self._id is not None
        return self._ipcClient.call('allocation__pool', id=self._id)

    def continent(self):
        assert self._id is not None
        return self._ipcClient.call('allocation__continent', id=self._id)

    def free(self):
        assert self._id is not None
        logging.info("freeing allocation")
        self._ipcClient.call('allocation__free', id=self._id)
        self._close()

    def assetKind(self):
        return self._assetKind

    def _close(self):
        self._heartbeat.unregister(self._id)
        self._id = None
        self._ipcClient.allocationClosed(self)

    def setForceReleaseCallback(self, callback):
        self._forceReleaseCallback = callback

    def connectionToProviderInterrupted(self):
        self._close()
