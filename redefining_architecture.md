It is about redefining the architecture and here is a proposed plan for the same. We will 
use a microservice based architecture where each micro service will operate on its own. 
We will be having a shared folder where they will connect with each other and used the shared architecture. 

.
|-- README.md
|-- demo.py
|-- packages.txt
|-- requirements.txt
|-- test_data
|   |-- Hindi.flac
|   |-- hello.txt
|   |-- hindi.pdf
|   |-- test.mp4
|   `-- ...
|-- audio_translation_service
|   |-- Dockerfile
|   |-- docker-compose.yml
|   |-- logs
|   |   |-- audio_processing.log
|   |-- requirements.txt
|   |-- src
|   |   |-- audio_utils.py
|   |   |-- main.py
|   `-- tests
|       |-- test_audio_translation.py
|-- video_translation_service
|   |-- Dockerfile
|   |-- docker-compose.yml
|   |-- logs
|   |   |-- video_processing.log
|   |-- requirements.txt
|   |-- src
|   |   |-- video_utils.py
|   |   |-- main.py
|   `-- tests
|       |-- test_video_translation.py
|-- text_translation_service
|   |-- Dockerfile
|   |-- docker-compose.yml
|   |-- logs
|   |   |-- txt_processing.log
|   |-- requirements.txt
|   |-- src
|   |   |-- txt_utils.py
|   |   |-- main.py
|   `-- tests
|       |-- test_text_translation.py
|-- utils
|   |-- common_utils.py
|   |-- translator.py
|-- api_gateway
|   |-- Dockerfile
|   |-- docker-compose.yml
|   |-- src
|   |   |-- gateway.py
|   `-- tests
|       |-- test_gateway.py
|-- monitoring
|   |-- Dockerfile
|   |-- docker-compose.yml
|   |-- src
|   |   |-- monitoring_service.py
|   `-- tests
|       |-- test_monitoring.py
`-- deployment
    |-- kubernetes
    |   |-- deployment.yaml
    |   |-- service.yaml
