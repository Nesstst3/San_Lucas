pipeline {
    agent any

    stages {
        stage('Clonar repo') {
            steps {
               git branch: 'main', url: 'https://github.com/Nesstst3/San_Lucas.git'
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
