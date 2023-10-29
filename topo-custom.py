#!/usr/bin/python



#  Copyright 2019-present Open Networking Foundation

#

#  Licensed under the Apache License, Version 2.0 (the "License");

#  you may not use this file except in compliance with the License.

#  You may obtain a copy of the License at

#

#      http://www.apache.org/licenses/LICENSE-2.0

#

#  Unless required by applicable law or agreed to in writing, software

#  distributed under the License is distributed on an "AS IS" BASIS,

#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

#  See the License for the specific language governing permissions and

#  limitations under the License.



import argparse



from mininet.cli import CLI

from mininet.log import setLogLevel

from mininet.net import Mininet

from mininet.node import Host

from mininet.topo import Topo

from stratum import StratumBmv2Switch



CPU_PORT = 255





class IPv4Host(Host):

    """Host that can be configured with an IPv4 gateway (default route).

    """



    def config(self, mac=None, ip=None, defaultRoute=None, lo='up', gw=None,

               **_params):

        super(IPv4Host, self).config(mac, ip, defaultRoute, lo, **_params)

        self.cmd('ip -4 addr flush dev %s' % self.defaultIntf())

        self.cmd('ip -6 addr flush dev %s' % self.defaultIntf())

        self.cmd('ip -4 link set up %s' % self.defaultIntf())

        self.cmd('ip -4 addr add %s dev %s' % (ip, self.defaultIntf()))

        if gw:

            self.cmd('ip -4 route add default via %s' % gw)

        # Disable offload

        for attr in ["rx", "tx", "sg"]:

            cmd = "/sbin/ethtool --offload %s %s off" % (

                self.defaultIntf(), attr)

            self.cmd(cmd)



        def updateIP():

            return ip.split('/')[0]



        self.defaultIntf().updateIP = updateIP





class TaggedIPv4Host(Host):

    """VLAN-tagged host that can be configured with an IPv4 gateway

    (default route).

    """

    vlanIntf = None



    def config(self, mac=None, ip=None, defaultRoute=None, lo='up', gw=None,

               vlan=None, **_params):

        super(TaggedIPv4Host, self).config(mac, ip, defaultRoute, lo, **_params)

        self.vlanIntf = "%s.%s" % (self.defaultIntf(), vlan)

        # Replace default interface with a tagged one

        self.cmd('ip -4 addr flush dev %s' % self.defaultIntf())

        self.cmd('ip -6 addr flush dev %s' % self.defaultIntf())

        self.cmd('ip -4 link add link %s name %s type vlan id %s' % (

            self.defaultIntf(), self.vlanIntf, vlan))

        self.cmd('ip -4 link set up %s' % self.vlanIntf)

        self.cmd('ip -4 addr add %s dev %s' % (ip, self.vlanIntf))

        if gw:

            self.cmd('ip -4 route add default via %s' % gw)



        self.defaultIntf().name = self.vlanIntf

        self.nameToIntf[self.vlanIntf] = self.defaultIntf()



        # Disable offload

        for attr in ["rx", "tx", "sg"]:

            cmd = "/sbin/ethtool --offload %s %s off" % (

                self.defaultIntf(), attr)

            self.cmd(cmd)



        def updateIP():

            return ip.split('/')[0]



        self.defaultIntf().updateIP = updateIP



    def terminate(self):

        self.cmd('ip -4 link remove link %s' % self.vlanIntf)

        super(TaggedIPv4Host, self).terminate()





class TutorialTopo(Topo):

    """4x3 fabric topology with IPv4 hosts"""



    def __init__(self, *args, **kwargs):

        Topo.__init__(self, *args, **kwargs)



        # Leaves

        # gRPC port 50001

        leaf1 = self.addSwitch('leaf1', cls=StratumBmv2Switch, cpuport=CPU_PORT)

        # gRPC port 50002

        leaf2 = self.addSwitch('leaf2', cls=StratumBmv2Switch, cpuport=CPU_PORT)

        # gRPC port 50003

        leaf3 = self.addSwitch('leaf3', cls=StratumBmv2Switch, cpuport=CPU_PORT)

        # gRPC port 50004

        leaf4 = self.addSwitch('leaf4', cls=StratumBmv2Switch, cpuport=CPU_PORT)



        # Spines

        # gRPC port 50005

        spine1 = self.addSwitch('spine1', cls=StratumBmv2Switch, cpuport=CPU_PORT)

        # gRPC port 50006

        spine2 = self.addSwitch('spine2', cls=StratumBmv2Switch, cpuport=CPU_PORT)

        # gRPC port 50007

        spine3 = self.addSwitch('spine3', cls=StratumBmv2Switch, cpuport=CPU_PORT)



        # Switch Links

        self.addLink(spine1, leaf1)

        self.addLink(spine1, leaf2)

        self.addLink(spine1, leaf3)

        self.addLink(spine1, leaf4)

        self.addLink(spine2, leaf1)

        self.addLink(spine2, leaf2)

        self.addLink(spine2, leaf3)

        self.addLink(spine2, leaf4)

        self.addLink(spine3, leaf1)

        self.addLink(spine3, leaf2)

        self.addLink(spine3, leaf3)

        self.addLink(spine3, leaf4)



        # IPv4 hosts attached to leaf 1

        h1a = self.addHost('h1a', cls=TaggedIPv4Host, mac="00:00:00:00:00:1A",

                          ip='172.16.1.1/24', gw='172.16.1.254', vlan=100)

        self.addLink(h1a, leaf1)  # port 4

        h1b = self.addHost('h1b', cls=TaggedIPv4Host, mac="00:00:00:00:00:1B",

                          ip='172.16.1.2/24', gw='172.16.1.254', vlan=100)

        self.addLink(h1b, leaf1)  # port 5

        h1c = self.addHost('h1c', cls=TaggedIPv4Host, mac="00:00:00:00:00:1C",

                          ip='172.16.1.3/24', gw='172.16.1.254', vlan=100)

        self.addLink(h1c, leaf1)  # port 6

        h1d = self.addHost('h1d', cls=TaggedIPv4Host, mac="00:00:00:00:00:1D",

                          ip='172.16.1.4/24', gw='172.16.1.254', vlan=100)

        self.addLink(h1d, leaf1)  # port 7



        # IPv4 hosts attached to leaf 2

        h2a = self.addHost('h2a', cls=TaggedIPv4Host, mac="00:00:00:00:00:2A",

                          ip='172.16.2.1/24', gw='172.16.2.254', vlan=200)

        self.addLink(h2a, leaf2)  # port 4

        h2b = self.addHost('h2b', cls=TaggedIPv4Host, mac="00:00:00:00:00:2B",

                          ip='172.16.2.2/24', gw='172.16.2.254', vlan=200)

        self.addLink(h2b, leaf2)  # port 5

        h2c = self.addHost('h2c', cls=TaggedIPv4Host, mac="00:00:00:00:00:2C",

                          ip='172.16.2.3/24', gw='172.16.2.254', vlan=200)

        self.addLink(h2c, leaf2)  # port 6

        h2d = self.addHost('h2d', cls=TaggedIPv4Host, mac="00:00:00:00:00:2D",

                          ip='172.16.2.4/24', gw='172.16.2.254', vlan=200)

        self.addLink(h2d, leaf2)  # port 7



        # IPv4 hosts attached to leaf 3

        h3a = self.addHost('h3a', cls=TaggedIPv4Host, mac="00:00:00:00:00:3A",

                          ip='172.16.3.1/24', gw='172.16.3.254', vlan=300)

        self.addLink(h3a, leaf3)  # port 4

        h3b = self.addHost('h3b', cls=TaggedIPv4Host, mac="00:00:00:00:00:3B",

                          ip='172.16.3.2/24', gw='172.16.3.254', vlan=300)

        self.addLink(h3b, leaf3)  # port 5

        h3c = self.addHost('h3c', cls=TaggedIPv4Host, mac="00:00:00:00:00:3C",

                          ip='172.16.3.3/24', gw='172.16.3.254', vlan=300)

        self.addLink(h3c, leaf3)  # port 6

        h3d = self.addHost('h3d', cls=TaggedIPv4Host, mac="00:00:00:00:00:3D",

                          ip='172.16.3.4/24', gw='172.16.3.254', vlan=300)

        self.addLink(h3d, leaf3)  # port 7



        # IPv4 hosts attached to leaf 4

        h4a = self.addHost('h4a', cls=TaggedIPv4Host, mac="00:00:00:00:00:4A",

                          ip='172.16.4.1/24', gw='172.16.4.254', vlan=400)

        self.addLink(h4a, leaf4)  # port 4

        h4b = self.addHost('h4b', cls=TaggedIPv4Host, mac="00:00:00:00:00:4B",

                          ip='172.16.4.2/24', gw='172.16.4.254', vlan=400)

        self.addLink(h4b, leaf4)  # port 5

        h4c = self.addHost('h4c', cls=TaggedIPv4Host, mac="00:00:00:00:00:4C",

                          ip='172.16.4.3/24', gw='172.16.4.254', vlan=400)

        self.addLink(h4c, leaf4)  # port 6

        h4d = self.addHost('h4d', cls=TaggedIPv4Host, mac="00:00:00:00:00:4D",

                          ip='172.16.4.4/24', gw='172.16.4.254', vlan=400)

        self.addLink(h4d, leaf4)  # port 7





def main():

    net = Mininet(topo=TutorialTopo(), controller=None)

    net.start()

    CLI(net)

    net.stop()

    print '#' * 80

    print 'ATTENTION: Mininet was stopped! Perhaps accidentally?'

    print 'No worries, it will restart automatically in a few seconds...'

    print 'To access again the Mininet CLI, use `make mn-cli`'

    print 'To detach from the CLI (without stopping), press Ctrl-D'

    print 'To permanently quit Mininet, use `make stop`'

    print '#' * 80





if __name__ == "__main__":

    parser = argparse.ArgumentParser(

        description='Mininet topology script for 4x3 fabric with stratum_bmv2 and IPv4 hosts')

    args = parser.parse_args()

    setLogLevel('info')



    main()

    
