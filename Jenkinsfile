pipeline {
    agent any

    stages {
        stage('Clonar repo') {
            steps {
                git 'https://github.com/casillpaulina150/San_Lucas.git'
            }
        }

        stage('Ver archivos') {
            steps {
                sh 'ls -la'
            }
        }

        stage('Probar Docker') {
            steps {
                sh 'docker ps'
            }
        }
    }
}