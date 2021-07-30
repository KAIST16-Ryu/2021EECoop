#
# Copyright 2018-2021 Elyra Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import autopep8
import os
import re
import tempfile
import time
import requests
import json

from black import format_str, FileMode
from datetime import datetime
from elyra._version import __version__
from elyra.metadata import MetadataManager
from elyra.pipeline import RuntimePipelineProcess, PipelineProcessor, PipelineProcessorResponse
from elyra.util.path import get_absolute_path
from jinja2 import Environment, PackageLoader
#from kfp import Client as ArgoClient
#from kfp import compiler as kfp_argo_compiler
#from kfp.aws import use_aws_secret
##from kfp_tekton import TektonClient, compiler as kfp_tekton_compiler
#from kfp_notebook.pipeline import NotebookOp
#from kfp_server_api.exceptions import ApiException
from urllib3.exceptions import LocationValueError, MaxRetryError


class DemoPipelineProcessor(RuntimePipelineProcess):
    _type = 'demoruntime'

    # Provide users with the ability to identify a writable directory in the
    # running container where the notebook | script is executed. The location
    # must exist and be known before the container is started.
    # Defaults to `/tmp`
    WCD = os.getenv('ELYRA_WRITABLE_CONTAINER_DIR', '/tmp').strip().rstrip('/')

    @property
    def type(self):
        return self._type

    def process(self, pipeline):
        """Runs a pipeline on Kubeflow Pipelines

        Each time a pipeline is processed, a new version
        is uploaded and run under the same experiment name.
        """
        self.log.info("working")
        t0_all = time.time()
        timestamp = datetime.now().strftime("%m%d%H%M%S")

        runtime_configuration = self._get_metadata_configuration(namespace=MetadataManager.NAMESPACE_RUNTIMES,
                                                                 name=pipeline.runtime_config)

        api_endpoint = runtime_configuration.metadata['api_endpoint']
        cos_endpoint = runtime_configuration.metadata['cos_endpoint']
        cos_bucket = runtime_configuration.metadata['cos_bucket']

        user_namespace = runtime_configuration.metadata.get('user_namespace')

        # TODO: try to encapsulate the info below
        api_username = runtime_configuration.metadata.get('api_username')
        api_password = runtime_configuration.metadata.get('api_password')

        engine = runtime_configuration.metadata.get('engine')

        pipeline_name = pipeline.name

        self.log_pipeline_info(pipeline_name, "submitting pipeline")
        with tempfile.TemporaryDirectory() as temp_dir:
            pipeline_path = os.path.join(temp_dir, f'{pipeline_name}.tar.gz')

            self.log.debug("Creating temp directory %s", temp_dir)

            self.log.debug("Kubeflow Pipeline was created in %s", pipeline_path)



            self._cc_pipeline(pipeline,pipeline_name)
            
            return DemoPipelineProcessorResponse(
                run_url=f'{api_endpoint}/#/runs/details',
                object_storage_url=f'{cos_endpoint}',
                object_storage_path=f'/{cos_bucket}',
            )

        return None

    def export(self, pipeline, pipeline_export_format, pipeline_export_path, overwrite):
        

        return None  # Return the input value, not its absolute form

    def _cc_pipeline(self,
                     pipeline,
                     pipeline_name,
                     cos_directory=None,
                     export=False):

        runtime_configuration = self._get_metadata_configuration(namespace=MetadataManager.NAMESPACE_RUNTIMES,
                                                                 name=pipeline.runtime_config)

        cos_endpoint = runtime_configuration.metadata['cos_endpoint']
        cos_username = runtime_configuration.metadata['cos_username']
        cos_password = runtime_configuration.metadata['cos_password']
        cos_secret = runtime_configuration.metadata.get('cos_secret')
        self.log.info(f"cos_endpoint={cos_endpoint}")
        self.log.info(f"cos_username={cos_username}")
        self.log.info(f"cos_password={cos_password}")
        self.log.info(f"cos_secret={cos_secret}")

        if cos_directory is None:
            cos_directory = pipeline_name
        cos_bucket = runtime_configuration.metadata['cos_bucket']


        # Sort operations based on dependency graph (topological order)
        sorted_operations = PipelineProcessor._sort_operations(pipeline.operations)

        # All previous operation outputs should be propagated throughout the pipeline.
        # In order to process this recursively, the current operation's inputs should be combined
        # from its parent's inputs (which, themselves are derived from the outputs of their parent)
        # and its parent's outputs.

        PipelineProcessor._propagate_operation_inputs_outputs(pipeline, sorted_operations)

        for operation in sorted_operations:


            sanitized_operation_name = self._sanitize_operation_name(operation.name)
            self.log.info(f"filename {operation.filename}")
            self.log.info(f"input {operation.inputs}")

        return None

    @staticmethod
    def _sanitize_operation_name(name: str) -> str:
        """
        In KFP, only letters, numbers, spaces, "_", and "-" are allowed in name.
        :param name: name of the operation
        """
        return re.sub('-+', '-', re.sub('[^-_0-9A-Za-z ]+', '-', name)).lstrip('-').rstrip('-')

    @staticmethod
    def _get_user_auth_session_cookie(url, username, password):
        get_response = requests.get(url)

        # auth request to kfp server with istio dex look like '/dex/auth/local?req=REQ_VALUE'
        if 'auth' in get_response.url:
            credentials = {'login': username, 'password': password}

            # Authenticate user
            session = requests.Session()
            session.post(get_response.url, data=credentials)
            cookie_auth_key = 'authservice_session'
            cookie_auth_value = session.cookies.get(cookie_auth_key)

            if cookie_auth_value:
                return cookie_auth_key + '=' + cookie_auth_value


class DemoPipelineProcessorResponse(PipelineProcessorResponse):

    _type = 'demoruntime'

    def __init__(self, run_url, object_storage_url, object_storage_path):
        super().__init__(run_url, object_storage_url, object_storage_path)

    @property
    def type(self):
        return self._type
