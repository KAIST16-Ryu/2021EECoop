# Description.
# Made by Ryu Eojin, Institue of Technology, Platform Department.

# DistributeTrain_PreTraining.py does the followings.
#

import argparse
import time

import kubernetes
from kubernetes import config, client

parser = argparse.ArgumentParser(description='Manager for distributed training set of pods',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--rand-num', type=int, default=999,
                            help='random number for label identification.')

def main() :
    args = parser.parse_args()
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    rand_num = '%03d' %(args.rand_num)
    target_labels = {"num": rand_num}
    target_namespace = "default"

    worker_pod_name = "distributetrain-worker-"+rand_num

    # Wait until the train is ended.
    ########################################################################################################
    while True :
        distributedtrain_pods = v1.list_namespaced_pod(namespace=target_namespace, label_selector="num=%s"%(rand_num)).items
        chief_worker_pod = distributedtrain_pods[0]

        terminated_status = chief_worker_pod.status.container_statuses[0].state.terminated

        if terminated_status != None :

            # Distributedtrain was ended succesfully.
            if terminated_status.reason == 'Completed' : break

            else :
                # Something wrong situation. Handle this.
                break
        
        else :
            time.sleep(20)
            print ("Not ended yet.")
            continue
    ########################################################################################################


    # Retrieve train pods.
    ########################################################################################################
    for distributedtrain_pod in distributedtrain_pods :
        pod_name = distributedtrain_pod.metadata.name
        pod_namespace = target_namespace
        
        try :
            v1.delete_namespaced_pod(name=pod_name, namespace=pod_namespace)
        except client.exceptions.ApiException :
            pass # You should handle this.
    ########################################################################################################
if __name__ == '__main__' :
    main()


