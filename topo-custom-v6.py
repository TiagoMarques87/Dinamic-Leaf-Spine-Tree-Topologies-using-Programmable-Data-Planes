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


class IPv6Host(Host):
    """Host that can be configured with an IPv6 gateway (default route).
    """

    def config(self, ipv6, ipv6_gw=None, **params):
        super(IPv6Host, self).config(**params)
        self.cmd('ip -4 addr flush dev %s' % self.defaultIntf())
        self.cmd('ip -6 addr flush dev %s' % self.defaultIntf())
        self.cmd('ip -6 addr add %s dev %s' % (ipv6, self.defaultIntf()))
        if ipv6_gw:
            self.cmd('ip -6 route add default via %s' % ipv6_gw)
        # Disable offload
        for attr in ["rx", "tx", "sg"]:
            cmd = "/sbin/ethtool --offload %s %s off" % (self.defaultIntf(), attr)
            self.cmd(cmd)

        def updateIP():
            return ipv6.split('/')[0]

        self.defaultIntf().updateIP = updateIP

    def terminate(self):
        super(IPv6Host, self).terminate()


class TutorialTopo(Topo):
    """4x3 fabric topology with IPv6 hosts"""

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

        # IPv6 hosts attached to leaf 1
        h1a = self.addHost('h1a', cls=IPv6Host, mac="00:00:00:00:00:1A",
                           ipv6='2001:1:1::a/64', ipv6_gw='2001:1:1::ff')
        h1b = self.addHost('h1b', cls=IPv6Host, mac="00:00:00:00:00:1B",
                           ipv6='2001:1:1::b/64', ipv6_gw='2001:1:1::ff')
        h1c = self.addHost('h1c', cls=IPv6Host, mac="00:00:00:00:00:1C",
                           ipv6='2001:1:1::c/64', ipv6_gw='2001:1:1::ff')
        h1d = self.addHost('h1d', cls=IPv6Host, mac="00:00:00:00:00:1D",
                           ipv6='2001:1:1::d/64', ipv6_gw='2001:1:1::ff')
        self.addLink(h1a, leaf1) # port 4
        self.addLink(h1b, leaf1) # port 5
        self.addLink(h1c, leaf1) # port 6
        self.addLink(h1d, leaf1) # port 7

        # IPv6 hosts attached to leaf 2
        h2a = self.addHost('h2a', cls=IPv6Host, mac="00:00:00:00:00:2A",
                           ipv6='2001:2:2::a/64', ipv6_gw='2001:2:2::ff')
        h2b = self.addHost('h2b', cls=IPv6Host, mac="00:00:00:00:00:2B",
                           ipv6='2001:2:2::b/64', ipv6_gw='2001:2:2::ff')
        h2c = self.addHost('h2c', cls=IPv6Host, mac="00:00:00:00:00:2C",
                           ipv6='2001:2:2::c/64', ipv6_gw='2001:2:2::ff')
        h2d = self.addHost('h2d', cls=IPv6Host, mac="00:00:00:00:00:2D",
                           ipv6='2001:2:2::d/64', ipv6_gw='2001:2:2::ff')
        self.addLink(h2a, leaf2) # port 4
        self.addLink(h2b, leaf2) # port 5
        self.addLink(h2c, leaf2) # port 6
        self.addLink(h2d, leaf2) # port 7

        # IPv6 hosts attached to leaf 3
        h3a = self.addHost('h3a', cls=IPv6Host, mac="00:00:00:00:00:3A",
                           ipv6='2001:3:3::a/64', ipv6_gw='2001:3:3::ff')
        h3b = self.addHost('h3b', cls=IPv6Host, mac="00:00:00:00:00:3B",
                           ipv6='2001:3:3::b/64', ipv6_gw='2001:3:3::ff')
        h3c = self.addHost('h3c', cls=IPv6Host, mac="00:00:00:00:00:3C",
                           ipv6='2001:3:3::c/64', ipv6_gw='2001:3:3::ff')
        h3d = self.addHost('h3d', cls=IPv6Host, mac="00:00:00:00:00:3D",
                           ipv6='2001:3:3::d/64', ipv6_gw='2001:3:3::ff')
        self.addLink(h3a, leaf3) # port 4
        self.addLink(h3b, leaf3) # port 5
        self.addLink(h3c, leaf3) # port 6
        self.addLink(h3d, leaf3) # port 7

        # IPv6 hosts attached to leaf 4
        h4a = self.addHost('h4a', cls=IPv6Host, mac="00:00:00:00:00:4A",
                           ipv6='2001:4:4::a/64', ipv6_gw='2001:4:4::ff')
        h4b = self.addHost('h4b', cls=IPv6Host, mac="00:00:00:00:00:4B",
                           ipv6='2001:4:4::b/64', ipv6_gw='2001:4:4::ff')
        h4c = self.addHost('h4c', cls=IPv6Host, mac="00:00:00:00:00:4C",
                           ipv6='2001:4:4::c/64', ipv6_gw='2001:4:4::ff')
        h4d = self.addHost('h4d', cls=IPv6Host, mac="00:00:00:00:00:4D",
                           ipv6='2001:4:4::d/64', ipv6_gw='2001:4:4::ff')
        self.addLink(h4a, leaf4) # port 4
        self.addLink(h4b, leaf4) # port 5
        self.addLink(h4c, leaf4) # port 6
        self.addLink(h4d, leaf4) # port 7


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
        description='Mininet topology script for 4x3 fabric with stratum_bmv2 and IPv6 hosts')
    args = parser.parse_args()
    setLogLevel('info')

    main()
