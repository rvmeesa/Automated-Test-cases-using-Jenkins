pipeline {
    agent any
    environment {
        APP_URL = "http://${env.EC2_PUBLIC_IP}:5000"
    }
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/JohnImmanuel305/Todo-app.git'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t todo-app-test:latest .'
            }
        }
        stage('Start App') {
            steps {
                sh 'python3 app.py &'
                sh 'sleep 5'
            }
        }
        stage('Run Tests') {
            agent {
                docker {
                    image 'todo-app-test:latest'
                    args '--network host'
                }
            }
            steps {
                sh 'pytest tests/test_todo_app.py --verbose --junitxml=test-reports/report.xml'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'test-reports/*.xml', allowEmptyArchive: true
            junit 'test-reports/*.xml'
            emailext (
                subject: "Jenkins Build ${env.BUILD_NUMBER} - ${currentBuild.currentResult}",
                body: "Test results for build ${env.BUILD_NUMBER} are attached. See details: ${env.BUILD_URL}",
                to: "${env.GIT_COMMITTER_EMAIL}",
                attachLog: true,
                attachmentsPattern: 'test-reports/*.xml'
            )
        }
    }
}