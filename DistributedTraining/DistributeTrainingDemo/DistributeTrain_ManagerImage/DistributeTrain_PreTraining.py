# Description.
# Made by Ryu Eojin, Institue of Technology, Platform Department.

# DistributeTrain_PreTraining.py does the followings.
#
# 1) Get available cluster gpus.
#   - 1. Get all gpus in the cluster.
#   - 2. Get all gpus that are in use.
#   - 3. Subtract (1.) and (2.), and get available gpus table.
#
# 2) Get some gpus among the available ones, and decide where to allocate them.
#    Use appropriate scheduling strategies (= Scheduling algorithms).
#   - 1. For now, just allocate pods to the node with largest number of gpus.
#   - 2. For now, just handle the case for one node, and 2 nodes cases.
#   - ( Hope you to update with better scheculing algorithms. )
#
# 3) Create worker pods. ( n-1 pods, n stands for the allocated nodes. )
#
# 4) Create necessary files for the chief worker pod.
#   ( myhostfile - it is used for "horovodrun" command. 
#             Ex) $ horovordun -np 2 -hostfile myhostfile ...)
#   ( config - it is used for OpenSSH communication between workers. )
#
# 5) Create chief worker pod. The last one. ((n-1) + 1 = n)
#
# 6) Initiate training with "horovodrun" command.

import argparse
import time
import kubernetes
from kubernetes import config, client

parser = argparse.ArgumentParser(
    description='Arguments of "DistributeTrain_PreTraining.py"',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument('--num-gpus', type=int, default=1,
                            help='number of gpus for distributed training.')
parser.add_argument('--rand-num', type=int, default=999,
                            help='random number for label identification.')
parser.add_argument('--image', type=str, default="neo21top/hvd_base_v1",
                    help='Base image name that you want to use.')
parser.add_argument('--port', type=int, default=12345,
                    help='Port number that you want to use.')
parser.add_argument('--filename', type=str, default='hvd_train.py',
                    help='Name of the training python script.')
parser.add_argument('--host-network', type=str, default=True,
                    help='Option to decide whether to use hostnetwork or not.')

IdentityFile = '~/.ssh/lifelog-lab-t3q.pem'

# Set default value.
############################################################################
args = parser.parse_args()

num_requested_gpus = args.num_gpus
rand_num = '%03d' %(args.rand_num)
target_labels = {"num": rand_num}
target_namespace = "default"
target_port = args.port
target_filename = '/examples/'+args.filename
target_host_network = 1

if args.host_network == "True" or args.host_network == "true" :
    target_host_network = 1
elif args.host_network == "False" or args.host_network == "false" :
    target_host_network = 0

worker_pod_name = "distributetrain-"+rand_num
############################################################################

def check_available_one_node(available_cluster_gpus, num_gpus) :
    for node_with_gpus in available_cluster_gpus[::-1] :
        if node_with_gpus[1] >= num_gpus :
            # return [(node_with_gpus[0], num_gpus)]
            return [num_gpus]

    return "Unavailable"

def check_available_two_node(available_cluster_gpus, num_gpus) :

    two_node = [available_cluster_gpus[0][1]]
    num_2nd_gpus = num_gpus - available_cluster_gpus[0][1]

    for node_with_gpus in available_cluster_gpus[:0:-1] :
        if node_with_gpus[1] >= num_2nd_gpus :
            two_node.append(num_2nd_gpus)
            return two_node
    
    return "Unavailable"

def get_all_cluster_gpus (v1) :
    # Get all cluster_gpus to the "cluster_gpus_all"
    ############################################################################
    cluster_gpus_all = {}
    
    for node in v1.list_node().items :
        for node_host in node.status.addresses :
            if node_host.type == 'Hostname' :
                cluster_gpus_all[node_host.address] \
                    = int(node.status.capacity['nvidia.com/gpu'])

    return cluster_gpus_all
    ############################################################################


def get_using_cluster_gpus (v1) :

    # Get using_cluster_gpus to the "cluster_gpus_on_use"
    ############################################################################
    cluster_gpus_on_use = {}

    all_pods = v1.list_pod_for_all_namespaces(watch=False).items

    for i in all_pods :
        pod_resources_limits = i.spec.containers[0].resources.limits
        if pod_resources_limits != None and i.status.phase != "Succeeded" :
            if pod_resources_limits.get('nvidia.com/gpu') != None  :
                node_of_pod = i.spec.node_name
                
                if cluster_gpus_on_use.get(node_of_pod) != None :
                    cluster_gpus_on_use[node_of_pod] \
                        += int(pod_resources_limits['nvidia.com/gpu'])

                else :
                    cluster_gpus_on_use[node_of_pod] \
                        = int(pod_resources_limits['nvidia.com/gpu'])

    return cluster_gpus_on_use
    ############################################################################


def sort_available_cluster_gpus (cluster_gpus_available_dict) :
    # "Sort" available_cluster_gpus for convenience in an "descending order".
    ############################################################################
    cluster_gpus_available = []

    for unsorted_node_gpus in cluster_gpus_available_dict.items() :
        added = False
        for j in range(len(cluster_gpus_available)) :
            if unsorted_node_gpus[1] > cluster_gpus_available[j][1] :
                cluster_gpus_available.insert(j, unsorted_node_gpus)
                added = True
                break

        if not added : cluster_gpus_available.append(unsorted_node_gpus)
    
    return cluster_gpus_available
    ###########################################################################
    

def get_available_cluster_gpus (v1) :

    # Get all cluster_gpus to the "cluster_gpus_all"
    # cluster_gpus_all is a "dictionary".
    # Ex )
    cluster_gpus_all = get_all_cluster_gpus(v1)
    
    # Get using_cluster_gpus to the "cluster_gpus_on_use"
    # cluster_gpus_on_use is a "dictionary".
    # Ex )
    cluster_gpus_on_use = get_using_cluster_gpus(v1)
    
    # Get available_cluster_gpus.
    # Subtract "cluster_gpus_all" - "cluster_gpus_on_use".
    ############################################################################
    cluster_gpus_available_dict = cluster_gpus_all.copy()
    num_available_gpus = 0

    for (node, num_gpus) in cluster_gpus_all.items() :
        if cluster_gpus_on_use.get(node) :
            cluster_gpus_available_dict[node] -= cluster_gpus_on_use[node]

            if cluster_gpus_available_dict[node] == 0 :
                del cluster_gpus_available_dict[node]
            
            else : num_available_gpus += cluster_gpus_available_dict[node]
        else : num_available_gpus += num_gpus
    ############################################################################

    # "Sort" available_cluster_gpus for convenience in an "descending order".
    cluster_gpus_available = sort_available_cluster_gpus(cluster_gpus_available_dict)

    return (cluster_gpus_available, num_available_gpus)
    ############################################################################


def schedule_gpus_to_nodes (available_cluster_gpus, available_num_gpus) :
    # You can make your own schedule algormthms.
    # What you have to do is....
    # if you get the gpu table of available node (descending order, Ex) [5, 3, 2, 1]),
    # and objective number of allocate gpus 4,
    # then you should schedule as [3, 1].
    ############################################################################
    table_allocate_gpus = []
    num_allocate_gpus = 0

    for num_gpus in range( available_num_gpus, 0, -1 ) :

        # Check whether you can allocate using 1 nodes,
        table_allocate_gpus \
            = check_available_one_node(available_cluster_gpus, num_gpus)
        if table_allocate_gpus != 'Unavailable' :
            num_allocate_gpus = num_gpus
            break

        # Check whether you can allocate using 2 nodes.
        table_allocate_gpus \
            = check_available_two_node(available_cluster_gpus, num_gpus)
        if table_allocate_gpus != 'Unavailable' :
            num_allocate_gpus = num_gpus
            break

        # You can make 3 or more nodes. But it may not efficient.
        # Apply here.
        
    if num_allocate_gpus == 0 :
        # There are no possible Scheduling for distributed training.
        # You should handle this such as ans Exception.

        # Handle it!
        pass

    return [table_allocate_gpus, num_gpus]
    ############################################################################


def create_worker_pods (table_allocate_gpus, v1) :
    ############################################################################
    for i in range(1, len(table_allocate_gpus)) :
        worker_resources = client.V1ResourceRequirements(
            limits={ "nvidia.com/gpu": "%d" %(table_allocate_gpus[i]) }
        )

        worker_container = client.V1Container(
            name=worker_pod_name,
            image=args.image,
            resources=worker_resources,
            command=["/bin/bash"],
            args=["-c", "/usr/sbin/sshd -p %d; sleep infinity" %(target_port)]
        )

        worker_pod_meta = client.V1ObjectMeta(
            name=worker_pod_name+'-%d'%(i),
            namespace=target_namespace,
            labels=target_labels
        )

        # If you want to specify "node_name", do it.
        worker_pod_spec = client.V1PodSpec(
            containers=[worker_container],
            host_network=bool(target_host_network)
        )

        worker_pod = client.V1Pod(
            api_version='v1',
            kind='Pod',
            metadata=worker_pod_meta,
            spec=worker_pod_spec
        )

        v1.create_namespaced_pod(namespace=target_namespace, body=worker_pod)
    ############################################################################

def create_chief_worker_pods (table_allocate_gpus, num_allocate_gpus, v1) :
    # Create appropriate worker pods, "myhostfile", and "Config".
    ############################################################################
    hostfile = "localhost slots=%d" %(table_allocate_gpus[0])
    configfile = ""

    worker_pod_ips = []
    # Create string for "myhostfile".
    for i in range(1, len(table_allocate_gpus)) :
        count = 0
        while True :
            try :
                time.sleep(1)
                count += 1
                api_response = v1.read_namespaced_pod (
                    name=worker_pod_name+'-%d'%(i),
                    namespace=target_namespace
                )

                # if do not use hostnetwork, it has some delay to give new ip.
                # continue and git more delay 1 seconds.
                if api_response.status.pod_ip == None :
                    continue 

                worker_pod_ips.append(api_response.status.pod_ip)
                hostfile += "\n%s slots=%d" \
                    %(worker_pod_ips[i-1], table_allocate_gpus[i])
                break

            except client.exceptions.ApiException :
                if count > 30 :
                    # Make your own error! 
                    # Ex) raise TimeOutException('Worker Pod does not created all.')
                    # print ("Not Good Situation.")
                    break
                else :
                    continue

    # Create string for "Config".
    for pod_ip in worker_pod_ips :
        configfile += "Host %s\n" %(pod_ip)
        configfile += "    HostName %s\n" %(pod_ip)
        configfile += "    User root\n"
        configfile += "    IdentityFile %s" %(IdentityFile)
        configfile += "\n\n"
    ############################################################################


    # Create worker pods.
    ############################################################################
    chief_worker_resources = client.V1ResourceRequirements(
        limits={ "nvidia.com/gpu": "%d" %(table_allocate_gpus[0]) }
    )

    chief_worker_container = client.V1Container(
        name=worker_pod_name,
        image=args.image,
        resources=chief_worker_resources,
        command = ["/bin/bash"],
        args = ["-c", "echo '%s' > /examples/myhostfile;\
                echo '%s' > ~/.ssh/config;\
                horovodrun -np %d -hostfile /examples/myhostfile -p %d python %s"
                %(hostfile, configfile, num_allocate_gpus, target_port, target_filename)]
    )

    chief_worker_pod_meta = client.V1ObjectMeta(
        name=worker_pod_name+'-0',
        namespace=target_namespace,
        labels=target_labels
    )

    # If you want to specify "node_name", do it.
    chief_worker_pod_spec = client.V1PodSpec(
        containers=[chief_worker_container],
        host_network=bool(target_host_network),
        restart_policy="OnFailure"
    )

    chief_worker_pod = client.V1Pod(
        api_version='v1',
        kind='Pod',
        metadata=chief_worker_pod_meta,
        spec=chief_worker_pod_spec
    )

    v1.create_namespaced_pod(namespace=target_namespace, body=chief_worker_pod)
    ############################################################################


def main () :
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    # Get available gpus in the cluster.
    # Ex ) available_cluster_gpus = [3, 1]
    # Ex ) available_num gpus = 4
    ############################################################################
    (available_cluster_gpus, available_num_gpus) = get_available_cluster_gpus(v1)
    #print ('available gpus in the cluster => ', available_cluster_gpus)
    #print ('available number of gpus in the cluster => ', available_num_gpus)
    ############################################################################


    # Scheduling appropriate node for distributed training.
    ############################################################################
    # Case when available gpus are short.
    if num_requested_gpus > available_num_gpus :
        # Decide whether just terminate, 
        # or continue training less with available gpus.
        print('There remains only %d gpus in the cluster.' %(available_num_gpus))

        # Handle this.
        pass

    # Scheduling appropriate node for distributed training.
    # As kubernetes allocate pod with random state, we don't have to 
    # specify the nodes. We just specify which number of gpus.
    # Ex) I want 4 gpus -> 3, 1 gpus can be splitted.
    # then, table_allocate_gpus, num_allocate_gpus are ...
    # table_allocate_gpus = [3, 1]
    # num_allocate_gpus = 4
    table_allocate_gpus = []
    num_allocate_gpus = 0

    table_allocate_gpus, num_allocate_gpus = schedule_gpus_to_nodes (
        available_cluster_gpus, 
        min(available_num_gpus, num_requested_gpus)
    )

    #print ('Will be scheduled node and gpu of the cluster => ', table_allocate_gpus)
    #print ('Will be scheduled number of gpus of the cluster => ', num_allocate_gpus)
    ############################################################################
    

    # Create worker pods.
    create_worker_pods (table_allocate_gpus, v1)

    # Create chief worker pods.
    if len(table_allocate_gpus > 1) :
        create_chief_worker_pods(table_allocate_gpus, num_allocate_gpus, v1)

if __name__ == '__main__' :
    main()


