pipeline {
    agent any

    stages {
        stage('Build Docker') {
            steps {
                sh 'docker build -t san_lucas .'
            }
        }

        stage('Stop container') {
            steps {
                sh 'docker stop sanlucas_app || true'
                sh 'docker rm sanlucas_app || true'
            }
        }

        stage('Run container') {
            steps {
                sh '''
                docker run -d -p 5000:5000 \
                --name sanlucas_app \
                san_lucas
                '''
            }
        }
    }
}
