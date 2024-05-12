pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                // Add build commands here
                echo 'Building..'
                sh 'make COVERAGE=1'
            }
        }
        stage('Test') {
            steps {
                // Add test commands here
                echo 'Testing..'
                sh 'make test COVERAGE=1'
            }
        }
    }
}