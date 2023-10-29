### LIBRARIES ###
from __future__ import division
import os


### CONSTANTS ###
DEVICE_FRAME_SIZE = 18                  # Number of lines until a given line occurs again in the device frame block
PORT_FRAME_SIZE = 13                    # Number of lines until a given line occurs again in the port frame block
HOST_FRAME_SIZE = 8                     # Number of lines until a given line occurs again in the host frame block
LEAF_IPV4_LOOPBACK = "192.168.1."       # IPv4 loopback address of leaf switches will follow the schema "192.168.1.X" (where X=number of the switch)
SPINE_IPV4_LOOPBACK = "192.168.2."      # IPv4 loopback address of spine switches will follow the schema "192.168.2.X" (where X=number of the switch)
LEAF_MAC = "00:AA:00:00:00:"            # MAC address of the leaf switches follow the schema "00:AA:00:00:00:XX" (where XX=number of the switch)
SPINE_MAC = "00:BB:00:00:00:"           # MAC address of the spine switches follow the schema "00:BB:00:00:00:XX" (where XX=number of the switch)
LEAF_MPLS_ID = "1"                      # MPLS ID of leaf switch follow the schema "1XX" (where XX=number of switch)
SPINE_MPLS_ID = "2"                     # MPLS ID of spine switch follow the schema "2XX" (where XX=number of switch)
LEAF_SAPCING = 200                      # Grid spacing between leaf switches
HOST_GATEWAY = "172.16.X.254"           # Hosts subnets will follow the schema "172.16.X.Y" (where X=number of switch; Y=interface [in this case gw=254])
HOST_MAC = "00:00:00:00:00:X"           # Hosts MAC will follow the schema "00:00:00:00:00:X" (where X=number of host)
HOST_IP = "172.16.X.Y"                  # Hosts IP will follow the schema "172.16.X.Y" (where X=number of leaf and Y=number of host)
START_LEAF_BLOCK = 98                   # Number of the line where the leaf block configuration starts for the mininet topology configuration file
ASCII_CONV = 32                         # Value to convert 'A' to 'a' or 'Z' to 'z'

### VARIABLES ###
gridX_Leaf = 200                        # XX cordinates of first leaf switch
gridY_Leaf = 0                          # YY cordinates of first leaf switch  (to be updated in grid_definition())
gridX_Spine = 0                         # XX cordinates of first spine switch (to be updated in grid_definition())
gridY_Spine = 200                       # TT cordinates of first spine switch
spine_spacing = 0                       # spacing between spine switches (to be updated in grid_definition())


### FUNCTIONS ###

""" Creates the file and writes the initial section of the frame
"""
def begin_of_file():
    file = open("mininet/netcfg-custom.json", 'w')
    file.write("{\n")
    file.close()

    topo_file = open("mininet/topo-custom.py", 'w')
    f_topo_v4_frame = open("mininet/mn_scripts/topo_v4_frame_header.txt", 'r')
    topo_v4_frame = f_topo_v4_frame.read()
    topo_file.write(topo_v4_frame)
    topo_file.close()
    f_topo_v4_frame.close()

    docker_file = open("docker-compose.yml", 'w')
    f_docker_frame = open("mininet/mn_scripts/docker_frame_header.txt", 'r')
    docker_frame = f_docker_frame.read()
    docker_file.write(docker_frame)
    docker_file.close()
    f_docker_frame.close()

    host_discovery_file = open("util/mn-host-discovery.sh", 'w')
    host_discovery_file.close()


""" Finalizes the general frame of the file and closes it 
"""
def end_of_file(leaf, spine):
    file = open("mininet/netcfg-custom.json", 'a')
    file.write("}")
    file.close()

    topo_file = open("mininet/topo-custom.py", 'a')
    f_topo_v4_frame = open("mininet/mn_scripts/topo_v4_frame_footer.txt", 'r')
    topo_v4_frame = f_topo_v4_frame.readlines()
    topo_v4_frame[16] = "        description='Mininet topology script for " + str(leaf) + 'x' + str(spine) + " fabric with stratum_bmv2 and IPv4 hosts')\n"
    topo_file.writelines(topo_v4_frame)
    topo_file.close()
    f_topo_v4_frame.close()

    docker_file = open("docker-compose.yml", 'a')
    f_docker_frame = open("mininet/mn_scripts/docker_frame_footer.txt", 'r')
    docker_frame = f_docker_frame.read()
    docker_file.write(docker_frame)
    docker_file.close()
    f_docker_frame.close()


""" Deals with the configuration of the configuration block of each device
"""
def devices_config(leaf, spine):
    global gridX_Leaf
    global gridX_Spine
    i = 1
    i_dev = 2
    i_gRPC = 4
    i_gridX = 8
    i_gridY = 9
    i_dev_name = 12
    i_ipv4_node_sid = 13
    i_ipv4_lb = 14
    i_mac = 15
    i_er = 16

    f_device_frame = open("mininet/mn_scripts/device_frame.txt", 'r')
    device_frame = f_device_frame.read()
    f_device_frame.close()

    file = open("mininet/netcfg-custom.json", 'a')
    file.write('  "devices": {\n')
    file.close()

    while(i <= leaf+spine):
        file = open("mininet/netcfg-custom.json", 'a')
        file.write(device_frame + ',\n')
        file.close()

        if(i <= leaf):
            replace_line("mininet/netcfg-custom.json", i_dev, '    "device:leaf' + str(i) + '": {\n')
            replace_line("mininet/netcfg-custom.json", i_gRPC, '        "managementAddress": "grpc://mininet:5' + str(i).zfill(4) + '?device_id=1",\n')
            replace_line("mininet/netcfg-custom.json", i_gridX, '        "gridX": ' + str(gridX_Leaf) + ',\n')
            replace_line("mininet/netcfg-custom.json", i_gridY, '        "gridY": ' + str(gridY_Leaf) + '\n')
            replace_line("mininet/netcfg-custom.json", i_dev_name, '        "name": "leaf' + str(i) + '",\n')
            replace_line("mininet/netcfg-custom.json", i_ipv4_node_sid, '        "ipv4NodeSid": ' + LEAF_MPLS_ID + str(i).zfill(2) + ',\n')
            replace_line("mininet/netcfg-custom.json", i_ipv4_lb, '        "ipv4Loopback": "' + LEAF_IPV4_LOOPBACK + str(i) + '",\n')
            replace_line("mininet/netcfg-custom.json", i_mac, '        "routerMac": "' + LEAF_MAC + str(i).zfill(2) + '",\n')
            gridX_Leaf = gridX_Leaf + LEAF_SAPCING

        else:
            replace_line("mininet/netcfg-custom.json", i_dev, '    "device:spine' + str(i-leaf) + '": {\n')
            replace_line("mininet/netcfg-custom.json", i_gRPC, '        "managementAddress": "grpc://mininet:5' + str(i).zfill(4) + '?device_id=1",\n')
            replace_line("mininet/netcfg-custom.json", i_gridX, '        "gridX": ' + str(gridX_Spine) + ',\n')
            replace_line("mininet/netcfg-custom.json", i_gridY, '        "gridY": ' + str(gridY_Spine) + '\n')
            replace_line("mininet/netcfg-custom.json", i_dev_name, '        "name": "spine' + str(i-leaf) + '",\n')
            replace_line("mininet/netcfg-custom.json", i_ipv4_node_sid, '        "ipv4NodeSid": ' + SPINE_MPLS_ID + str(i-leaf).zfill(2) + ',\n')
            replace_line("mininet/netcfg-custom.json", i_ipv4_lb, '        "ipv4Loopback": "' + SPINE_IPV4_LOOPBACK + str(i-leaf) + '",\n')
            replace_line("mininet/netcfg-custom.json", i_mac, '        "routerMac": "' + SPINE_MAC + str(i-leaf).zfill(2) + '",\n')
            replace_line("mininet/netcfg-custom.json", i_er, '        "isEdgeRouter": false,\n')
            gridX_Spine = gridX_Spine + spine_spacing
            
            if(i == leaf+spine):    # last loop of the cicle                
                remove_last_char("mininet/netcfg-custom.json")
        
        i = i + 1
        i_dev = i_dev + DEVICE_FRAME_SIZE
        i_gRPC = i_gRPC + DEVICE_FRAME_SIZE
        i_gridX = i_gridX + DEVICE_FRAME_SIZE
        i_gridY = i_gridY + DEVICE_FRAME_SIZE
        i_dev_name = i_dev_name + DEVICE_FRAME_SIZE
        i_ipv4_node_sid = i_ipv4_node_sid + DEVICE_FRAME_SIZE
        i_ipv4_lb = i_ipv4_lb + DEVICE_FRAME_SIZE
        i_mac = i_mac + DEVICE_FRAME_SIZE
        i_er = i_er + DEVICE_FRAME_SIZE

    file = open("mininet/netcfg-custom.json", 'a')
    file.write("}\n  },\n")
    file.close()


""" Deals with the configuration of the configuration block of each port interface
"""
def ports_config(leaf, spine):
    i = 1
    begin_port_config = 4 + (leaf + spine) * DEVICE_FRAME_SIZE      # math to discover the first line of the port config block
    i_port = begin_port_config
    i_port_name = begin_port_config + 3
    i_port_ip = begin_port_config + 5
    i_port_vlan = begin_port_config + 8
    
    f_port_frame = open("mininet/mn_scripts/port_frame.txt", 'r')
    port_frame = f_port_frame.read()
    f_port_frame.close()

    file = open("mininet/netcfg-custom.json", 'a')
    file.write('  "ports": {\n')
    file.close()

    while(i<=leaf):
        j = 1
        while(j<=host):
            file = open("mininet/netcfg-custom.json", 'a')
            file.write(port_frame + ',\n')
            file.close()

            replace_line("mininet/netcfg-custom.json", i_port, '    "device:leaf' + str(i) + '/' + str(spine+j) + '": {\n')
            replace_line("mininet/netcfg-custom.json", i_port_name, '          "name": "leaf' + str(i) + '-' + str(spine+j) + '",\n')
            replace_line("mininet/netcfg-custom.json", i_port_ip, '            "' + HOST_GATEWAY.replace("X", str(i)) + '/24"\n')
            replace_line("mininet/netcfg-custom.json", i_port_vlan, '            ' + str(i) + "".ljust(2,'0') + '\n')

            j += 1
            i_port += PORT_FRAME_SIZE
            i_port_name += PORT_FRAME_SIZE
            i_port_ip += PORT_FRAME_SIZE
            i_port_vlan += PORT_FRAME_SIZE
        i += 1
   
    remove_last_char("mininet/netcfg-custom.json")
    file = open("mininet/netcfg-custom.json", 'a')
    file.write("}\n  },\n")
    file.close()


""" Deals with the configuration of the configuration block of each host
"""
def hosts_config(leaf, spine):
    i = 1
    begin_host_config = find_EOF("mininet/netcfg-custom.json") + 1
    i_host_mac = begin_host_config 
    i_host_name = begin_host_config + 2
    i_gridX = begin_host_config + 4
    i_gridY = begin_host_config + 5
    gridX = 200
    gridY = gridY_Leaf + 100

    f_host_frame = open("mininet/mn_scripts/host_frame.txt", 'r')
    host_frame = f_host_frame.read()
    f_host_frame.close()

    file = open("mininet/netcfg-custom.json", 'a')
    file.write('  "hosts": {\n')
    file.close()

    while(i<=leaf):
        j = 1
        letter = ord('A')
        while(j<=host):
            file = open("mininet/netcfg-custom.json", 'a')
            file.write(host_frame + ',\n')
            file.close()

            replace_line("mininet/netcfg-custom.json", i_host_mac, '   "' + HOST_MAC.replace("X", str(i) + chr(letter)) + '/' + str(i) + "".ljust(2,'0') + '": {\n')
            replace_line("mininet/netcfg-custom.json", i_host_name, '        "name": "h' + str(i) + chr(letter + ASCII_CONV) + '",\n')
            if (j%3 == 1): replace_line("mininet/netcfg-custom.json", i_gridX, '       "gridX": ' + str(gridX-50) + ',\n')
            elif (j%3 == 2): replace_line("mininet/netcfg-custom.json", i_gridX, '       "gridX": ' + str(gridX) + ',\n')
            else: replace_line("mininet/netcfg-custom.json", i_gridX, '       "gridX": ' + str(gridX+50) + ',\n')
            replace_line("mininet/netcfg-custom.json", i_gridY, '       "gridY":' + str(gridY) + '\n') if (j/3 <= 1) else replace_line("mininet/netcfg-custom.json", i_gridY, '       "gridY":' + str(gridY + 100) + '\n')

            j += 1
            letter += 1
            i_host_mac += HOST_FRAME_SIZE 
            i_host_name += HOST_FRAME_SIZE
            i_gridX += HOST_FRAME_SIZE
            i_gridY += HOST_FRAME_SIZE
        gridX += LEAF_SAPCING    
        i = i + 1
    
    remove_last_char("mininet/netcfg-custom.json")
    file = open("mininet/netcfg-custom.json", 'a')
    file.write("}\n  }\n")
    file.close()    


""" Deals with the topology of the mininet (second script generated)
"""
def topology_config(leaf, spine):
    i = 1
    j = 1
    leaf_block = "        # Leaves\n"
    spine_block = "        # Spines\n"
    link_block = "        # Switch Links\n"
    host_block = "        # IPv4 hosts attached to leaf 1\n"

    topo_file = open("mininet/topo-custom.py", 'a')
    
    replace_line("mininet/topo-custom.py", 93, '    """' + str(leaf) + 'x' + str(spine) + ' fabric topology with IPv4 hosts"""\n')

    while(i<=leaf):
        leaf_block += '        # gRPC port 5' + str(i).zfill(4) + '\n'
        leaf_block += '        leaf' + str(i) + ' = self.addSwitch(' + "'leaf" + str(i) + "', cls=StratumBmv2Switch, cpuport=CPU_PORT)\n"
        i += 1
    topo_file.write(leaf_block)

    while(i<=leaf+spine):
        spine_block += '        # gRPC port 5' + str(i).zfill(4) + '\n'
        spine_block += '        spine' + str(i-leaf) + ' = self.addSwitch(' + "'spine" + str(i-leaf) + "', cls=StratumBmv2Switch, cpuport=CPU_PORT)\n"
        i += 1
    topo_file.write('\n' + spine_block)
    
    i=1
    while(i<=spine):
        j = 1
        while(j<=leaf):
            link_block += '        self.addLink(spine' + str(i) + ', leaf' + str(j) + ')\n'
            j += 1
        i += 1
    topo_file.write('\n' + link_block)

    i=1
    while(i<=leaf):
        j=1
        letter = ord('A')
        while(j<=host):
            host_block += '        h' + str(i) + chr(letter + ASCII_CONV) + " = self.addHost('h" + str(i) + chr(letter + ASCII_CONV) + "', cls=TaggedIPv4Host, mac=" + '"' + HOST_MAC.replace("X", str(i) + chr(letter)) + '",\n'
            host_block += "                          ip='" + HOST_IP.replace("X", str(i)).replace("Y", str(j)) + "/24', gw='" + HOST_GATEWAY.replace("X", str(i)) + "', vlan=" + str(i) + "".ljust(2,'0') + ')\n'
            host_block += '        self.addLink(h' + str(i) + chr(letter + ASCII_CONV) + ', leaf' + str(i) +')  # port ' + str(spine+j) + '\n'
            letter += 1
            j += 1
        if(i!=leaf):
            host_block += '\n        # IPv4 hosts attached to leaf ' + str(i+1) + "\n"
        i += 1
    host_block += '\n'
    topo_file.write('\n' + host_block + '\n')


""" Deals with the docker-compose.yml file configuration, namely, the gRPC ports needed for a given mininet topology
"""
def docker_config(leaf, spine):
    i = 1
    ports_block = ""

    docker_file = open("docker-compose.yml", 'a')

    while(i <= leaf+spine):
        ports_block += '      - "5' + str(i).zfill(4) + ':5' + str(i).zfill(4) + '"\n'
        i += 1
    docker_file.write(ports_block)


""" Generates a script to automate the host location discovery in mininet
"""
def host_discovery_script():
    host_discovery_file = open("util/mn-host-discovery.sh", 'a')
    i = 1
    data = ''

    while(i<=leaf):
        j = 1
        letter = ord('A')
        while(j<=host):
            data += "util/mn-cmd h" + str(i) + chr(letter + ASCII_CONV) + " ping -c 1 " + HOST_GATEWAY.replace("X", str(i)) + " > /dev/null\n"
            letter += 1
            j += 1
        i += 1
    host_discovery_file.write(data)


""" Auxiliary function that replaces a given line
    Input: name of the file to be changed; number of the line to be replaced; string with the text to be replaced
""" 
def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()


""" Auxiliary function that defines the position of all switches
    Input: number of leaf switches; number of spine switches
"""
def grid_definition(leaf, spine):
    global spine_spacing
    global offset
    global gridY_Leaf
    global gridX_Spine
    leaf_len = (leaf - 1) * 200
    spine_spacing = leaf_len // spine
    offset = spine_spacing // 2
    gridY_Leaf = gridY_Spine + spine_spacing
    gridX_Spine = gridX_Leaf + offset


""" Auxiliary function that removes last char of a given file
    Input: file that will have its last character removed
"""
def remove_last_char(file_name):
        f = open(file_name, 'rb+')
        f.seek(-3, 2)    # moves the cursor to the last character of the file
        f.truncate()     # resizes the file to not include the last character (removes last character from the file)
        f.close()    


""" Auxiliary function that returns the line number of a given expression/word
    Input: file used for the lookup 
"""
def find_EOF(file_name):
    f = open(file_name, 'rb+')
    data = f.readlines()
    return len(data)


""" Main funcion
"""
if __name__ == "__main__":
    leaf = int(os.environ['leafs'])
    spine = int(os.environ['spines'])
    host = int(os.environ['hosts'])
    grid_definition(leaf, spine)
    begin_of_file()
    devices_config(leaf, spine)
    ports_config(leaf, spine)
    hosts_config(leaf, spine)
    topology_config(leaf, spine)
    docker_config(leaf, spine)
    host_discovery_script()
    end_of_file(leaf,spine)
