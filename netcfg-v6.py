### LIBRARIES ###
from __future__ import division
import os


### CONSTANTS ###
LEAF_SAPCING = 200                      # Grid spacing between leaf switches
ASCII_CONV = 32                         # Value to convert 'A' to 'a' or 'Z' to 'z'


### VARIABLES ###
gridX_Leaf = 200                        # XX cordinates of first leaf switch
gridY_Leaf = 0                          # YY cordinates of first leaf switch  (to be updated in grid_definition())
gridX_Spine = 0                         # XX cordinates of first spine switch (to be updated in grid_definition())
gridY_Spine = 200                       # YY cordinates of first spine switch
spine_spacing = 0                       # spacing between spine switches (to be updated in grid_definition())
device_default = '''
    "device:leaf*": {
      "basic": {
        "managementAddress": "grpc://mininet:5*?device_id=1",
        "driver": "stratum-bmv2",
        "pipeconf": "org.onosproject.ngsdn-tutorial",
        "locType": "grid",
        "gridX": *,
        "gridY": *
      },
      "fabricDeviceConfig": {
        "myStationMac": "00:*:00:00:00:%",
        "mySid": "3:*%:2::",
        "isSpine": *
      }
    },
    '''
port_default = '''
    "device:leaf*/%": {
      "interfaces": [
        {
          "name": "leaf*-%",
          "ips": ["2001:*:*::ff/64"]
        }
      ]
    },
    '''
host_default = '''
    "00:00:00:00:00:*%/None": {
      "basic": {
        "name": "h*%",
        "locType": "grid",
        "gridX": *,
        "gridY": *
      }
    },
    '''
leaf_default = '''
        # gRPC port 5*
        leaf* = self.addSwitch('leaf*', cls=StratumBmv2Switch, cpuport=CPU_PORT)
        '''
spine_default = '''
        # gRPC port 5*
        spine* = self.addSwitch('spine*', cls=StratumBmv2Switch, cpuport=CPU_PORT)
        '''
link_default = '''
        self.addLink(*, leaf%)'''
host_config = '''
        h*% = self.addHost('h*%', cls=IPv6Host, mac="00:00:00:00:00:*$",
                           ipv6='2001:*:*::%/64', ipv6_gw='2001:*:*::ff')
        '''
host_discovery_default = 'util/mn-cmd h*% ping -c 1 2001:*:*::ff > /dev/null'


### FUNCTIONS ###
""" Creates the file and writes the initial section of the frame
"""
def begin_of_file():
    # creates the netcfg file
    netcfg_file = open("mininet/netcfg-custom-v6.json", 'w')
    netcfg_file.write("{\n")
    netcfg_file.close()

    # creates the topo file
    topo_file = open("mininet/topo-custom-v6.py", 'w')
    topo_file.close()

    # creates script for host descovery    
    host_discovery_file = open("util/mn-host-discovery-v6.sh", 'w')
    host_discovery_file.close()


""" Finalizes the general frame of the file and closes it 
"""
def end_of_file():
    # ends the netcfg file
    netcfg_file = open("mininet/netcfg-custom-v6.json", 'a')
    netcfg_file.write("\n}")
    netcfg_file.close()

    # ends the topo file
    topo_file = open("mininet/topo-custom-v6.py", 'a')
    # reads all the lines from the footer topology_v6 frame to an array and changes a single line to the correct leaf-spine values
    topo_v6_frame_footer_file = open("mininet/mn_scripts/topo_v6_frame_footer.txt", 'r')
    topo_v6_frame_footer = topo_v6_frame_footer_file.readlines()
    topo_v6_frame_footer[-5] = topo_v6_frame_footer[-5].replace('*', str(leaf)).replace('%', str(spine))
    topo_v6_frame_footer = ''.join(topo_v6_frame_footer)
    # writes the read lines to the topo file
    topo_file.write(topo_v6_frame_footer)
    # closes both files
    topo_file.close()
    topo_v6_frame_footer_file.close()



""" Auxiliary function that defines the position of all switches
    Input: number of leaf switches; number of spine switches
"""
def grid_definition():
    global spine_spacing
    global offset
    global gridY_Leaf
    global gridX_Spine
    leaf_len = (leaf - 1) * 200
    spine_spacing = leaf_len // spine
    offset = spine_spacing // 2
    gridY_Leaf = gridY_Spine + spine_spacing
    gridX_Spine = gridX_Leaf + offset


""" Deals with the configuration of the configuration block of each device
"""
def devices_config():
    global gridX_Leaf
    global gridX_Spine
    i = 1
    # begining of the devices block
    netcfg_file = open("mininet/netcfg-custom-v6.json", 'a')
    netcfg_file.write('  "devices": {')

    while i <= leaf + spine:
        new_device = device_default.split('\n')
        new_device[3] = new_device[3].replace('*', str(i).zfill(4))
        if i <= leaf: 
            new_device[1] = new_device[1].replace('*', str(i))
            new_device[7] = new_device[7].replace('*', str(gridX_Leaf))
            new_device[8] = new_device[8].replace('*', str(gridY_Leaf))
            new_device[11] = new_device[11].replace('*', 'aa').replace('%', str(i).zfill(2))
            new_device[12] = new_device[12].replace('*', '1').replace('%', str(i).zfill(2))
            new_device[13] = new_device[13].replace('*', 'false')
            gridX_Leaf += LEAF_SAPCING # update XX coordinates of next leaf (YY not need beacuse it is always the same)
        else:
            new_device[1] = new_device[1].replace('leaf', 'spine').replace('*', str(i-leaf))
            new_device[7] = new_device[7].replace('*', str(gridX_Spine))
            new_device[8] = new_device[8].replace('*', str(gridY_Spine))
            new_device[11] = new_device[11].replace('*', 'bb').replace('%', str(i-leaf).zfill(2))
            new_device[12] = new_device[12].replace('*', '2').replace('%', str(i-leaf).zfill(2))
            new_device[13] = new_device[13].replace('*', 'true')
            gridX_Spine += spine_spacing # update XX coordinates of next spine (YY not need beacuse it is always the same)

        new_device = '\n'.join(new_device[:-1]) # removes last \n (space between devices config) and converts the array back to a string
        if i == leaf + spine: # removes the ',' in the last device config and closes the bracket '}' on the whole device block
            new_device = new_device[:-1] + '\n  },\n'
        i += 1
        netcfg_file.write(new_device)

    netcfg_file.close()


""" Deals with the configuration of the configuration block of each port interface
"""
def ports_config():
    i = 1
    # begining of the devices block
    netcfg_file = open("mininet/netcfg-custom-v6.json", 'a')
    netcfg_file.write('  "ports": {')

    while i <= leaf:
        j = 1
        while j <= host:
            new_port = port_default.split('\n')
            new_port[1] = new_port[1].replace('*', str(i)).replace('%', str(spine + j))
            new_port[4] = new_port[4].replace('*', str(i)).replace('%', str(spine + j))
            new_port[5] = new_port[5].replace('*', str(i))
            new_port = '\n'.join(new_port[:-1]) # removes last \n (space between ports config) and converts the array back to a string
            if i == leaf and j == host: # removes the ',' in the last port config and closes the bracket '}' on the whole port block
                new_port = new_port[:-1] + '\n  },\n'
            j += 1
            netcfg_file.write(new_port)

        i += 1

    netcfg_file.close()


""" Deals with the configuration of the configuration block of each host
"""
def hosts_config():
    i = 1
    gridX = 200
    gridY = gridY_Leaf + 100
    # begining of the devices block
    netcfg_file = open("mininet/netcfg-custom-v6.json", 'a')
    netcfg_file.write('  "hosts": {')

    while i <= leaf:
        j = 1
        host_id = ord('A') # letter to identify each host on a given leaf
        while j <= host:
            new_host = host_default.split('\n')
            new_host[1] = new_host[1].replace('*', str(i)).replace('%', chr(host_id))
            new_host[3] = new_host[3].replace('*', str(i)).replace('%', chr(host_id + ASCII_CONV))

            # Math to place the hosts in the correct grid position
            if (j%3 == 1): new_host[5] = new_host[5].replace('*', str(gridX-50)) # 1st column
            elif (j%3 == 2): new_host[5] = new_host[5].replace('*', str(gridX)) # 2nd column
            else: new_host[5] = new_host[5].replace('*', str(gridX+50)) # 3rd column
            if (j/3 <= 1): new_host[6] = new_host[6].replace('*', str(gridY)) # 1st line
            else: new_host[6] = new_host[6].replace('*', str(gridY + 100)) # 2nd line

            new_host = '\n'.join(new_host[:-1]) # removes last \n (space between hosts config) and converts the array back to a string
            if i == leaf and j == host: # removes the ',' in the last host config and closes the bracket '}' on the whole host block
                new_host = new_host[:-1] + '\n  }'
            j += 1
            host_id += 1
            netcfg_file.write(new_host)

        gridX += LEAF_SAPCING
        i += 1

    netcfg_file.close()


""" Deals with the topology of the mininet (second script generated)
"""
def topology_config():
    i = 1

    # open the toppology file created in the "begin_of_file()" funtion
    topo_file = open("mininet/topo-custom-v6.py", 'a')
    # reads all the lines from the header topology_v6 frame to an array
    topo_v6_frame_header_file = open("mininet/mn_scripts/topo_v6_frame_header.txt", 'r')
    topo = topo_v6_frame_header_file.readlines()
    topo_v6_frame_header_file.close()
    # replaces the line with "*x% fabric topology with IPv6 hosts" to the correct values of leaf and spine (JUST PRESENTABLE)
    topo[-5] = topo[-5].replace('*', str(leaf)).replace('%', str(spine))
    # converts the array back to a string
    topo = ''.join(topo)
    topo_file.write(topo)
    
    # leaves configuration
    topo_file.write('        # Leaves')
    while i <= leaf:
        new_leaf = leaf_default.split('\n')
        new_leaf[1] = new_leaf[1].replace('*', str(i).zfill(4))
        new_leaf[2] = new_leaf[2].replace('*', str(i))
        # converts the array back to a string
        new_leaf = '\n'.join(new_leaf[:-1])
        topo_file.write(new_leaf)
        i += 1
    
    # spines configuration
    topo_file.write('\n\n        # Spines')
    while i <= leaf + spine:
        new_spine = spine_default.split('\n')
        new_spine[1] = new_spine[1].replace('*', str(i).zfill(4))
        new_spine[2] = new_spine[2].replace('*', str(i-leaf))
        # converts the array back to a string
        new_spine = '\n'.join(new_spine[:-1])
        topo_file.write(new_spine)
        i += 1

    # links configuration
    topo_file.write('\n\n        # Switch Links')
    i = 1
    while i <= spine:
        j = 1
        while j <= leaf:
            new_link = link_default.replace('*', 'spine' + str(i)).replace('%', str(j))
            j += 1
            topo_file.write(new_link)
        i += 1
    
    # host configuration
    i = 1
    while i <= leaf:
        topo_file.write('\n\n        # IPv6 hosts attached to leaf ' + str(i))
        j = 1
        host_id = ord('A') # letter to identify each host on a given leaf
        new_link = ''
        while j <= host:
            new_host = host_config.split('\n')
            new_host[1] = new_host[1].replace('*', str(i)).replace('%', chr(host_id + ASCII_CONV)).replace('$', chr(host_id))
            new_host[2] = new_host[2].replace('*', str(i)).replace('%', chr(host_id + ASCII_CONV))
            new_link += link_default.replace('*', 'h' + str(i) + chr(host_id + ASCII_CONV)).replace('%', str(i)) + ' # port ' + str(spine + j)
            new_host = '\n'.join(new_host[:-1])
            topo_file.write(new_host)
            j += 1
            host_id += 1
        topo_file.write(new_link)
        i += 1
    
    # closes the file after everything is written
    topo_file.close()


""" Generates a script to automate the host location discovery in mininet
"""
def host_discovery_script():
    host_discovery_file = open("util/mn-host-discovery-v6.sh", 'a')
    i = 1

    while(i<=leaf):
        j = 1
        host_id = ord('a') # letter to identify each host on a given leaf
        while(j<=host):
            new_host_discovery = host_discovery_default.replace('*', str(i)).replace('%', chr(host_id))
            host_id += 1
            j += 1
            host_discovery_file.write(new_host_discovery + '\n')
        i += 1


""" Main funcion
"""
if __name__ == "__main__":
    leaf = int(os.environ['leafs'])
    spine = int(os.environ['spines'])
    host = int(os.environ['hosts'])
    grid_definition()
    begin_of_file()
    devices_config()
    ports_config()
    hosts_config()
    topology_config()
    host_discovery_script()
    end_of_file()
