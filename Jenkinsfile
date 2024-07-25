pipeline {
    agent any
    options {
        // Clean the workspace before the build starts
        cleanWs()
    }
    stages {
        stage('Build') {
            steps {
                // Add build commands here
                echo 'Building..'
                sh 'cd cppcheck_project && make clean && make COVERAGE=1'
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