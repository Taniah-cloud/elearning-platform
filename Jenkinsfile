pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git branch: 'master',
                    url: 'https://github.com/Taniah-cloud/elearning-platform.git'
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build('elearning-app')
                }
            }
        }
        stage('Stop old container') {
            steps {
                script {
                    sh 'docker stop elearning-app || true'
                    sh 'docker rm elearning-app || true'
                }
            }
        }
        stage('Run new container') {
            steps {
                script {
                    docker.image('elearning-app').run('-p 8000:8000 --name elearning-app')
                }
            }
        }
        stage('Health Check') {
            steps {
                script {
                    sh 'sleep 5'
                    sh 'curl -f http://localhost:8000 || exit 1'
                }
            }
        }
    }
}
