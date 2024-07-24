pipeline {
    agent {
        docker {
            image 'ubuntu:latest'
            args '-u root:root' 
        }
    }

    stages {
        stage('Build') {
            steps {
                // Add build commands here
                echo 'Building..'
                sh 'cd cppcheck_project && make COVERAGE=1'
            }
        }
        stage('Test') {
            steps {
                // Add test commands here
                echo 'Testing..'
                sh 'cd cppcheck_project && make test COVERAGE=1'
            }
        }
    }
}