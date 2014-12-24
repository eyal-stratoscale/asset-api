VERSION = 1


class Client:
    """
    To create a client:
    from asset import clientfactory
    client = clientfactory.factory()
    make sure you have /etc/asset.conf in place
    """
    def allocate(self, assetKind, assetCount=1, pool=None, continent=None, allocationInfo=None):
        """
        Create an allocation of <assetCount> X <assetKind>.
        assertKind is just a string. Examples: subnet, vlan. Depends on
        what assets are defined in the asset provider (Server side).
        pool if defined, is in case there are two pools of the same
        resource. For example, subnets on the 1G network, or subnet on the
        10G network.
        continent, when specified, defines the releam - for example, if the
        test framework has two sites.
        allocationInfo is an object of type AllocationInfo, or None to use
        defaults from /etc/asset.conf
        """
        assert False, "Deriving class must implement"

    def setConnectionToProviderInterruptedCallback(self, callback):
        """
        the callback will be called (zero parameters) when the provider stops
        responding to heartbeats. This is not mandatory, the default behaviour
        is to SIGTERM this process.
        This is mainly useful for writing daemons that allocate resources, not
        for testing and scripts
        """
        assert False, "Deriving class must implement"


class AllocationInfo:
    def __init__(self, user, purpose, nice=0, comment=""):
        """
        This object represents what is this allocation for, by whom.
        This is important only for scheduling of shared resources

        user can be a name, or 'continuous integration', or 'QA'

        purpose can be:
        - 'build'
        - 'bare metal host for rack test'
        - 'vm runner for virtual rack test' (==slave)
        note: the last option is used to provision a CI slave, which
        means a virtual rack provider will be running on it.

        nice value: if you are writing a gready system, for example,
        a system for using as many free nodes as possible to run as
        many concurrent tests as possible, make sure to use increment
        this value for each additional allocation. expected values
        are between 0 and 1.
        """
        self.user = user
        self.purpose = purpose
        self.nice = nice
        self.comment = comment


class Allocation:
    """
    This object is returned from the Client.allocate method
    """
    def assets(self):
        """
        Returns an array of dictionaries describing the resources
        allocated, as described in the asset server.
        """
        assert False, "Deriving class must implement"

    def free(self):
        """
        free the allocation. After this was called, the application
        may not use any of the assets returned previously by the assets
        method, or call assets again
        """
        assert False, "Deriving class must implement"

    def assetKind(self):
        """
        retreives the assetKind requested when creating the allocations
        """
        assert False, "Deriving class must implement"

    def pool(self):
        """
        retrieve the pool id of assetKind resources that these assets were allocated from
        """
        assert False, "Deriving class must implement"

    def continent(self):
        """
        retrieve the continent id that these assets were allocated from
        """
        assert False, "Deriving class must implement"

    def setForceReleaseCallback(self, callback):
        assert False, "Deriving class must implement"
