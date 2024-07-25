pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                // Add build commands here
                echo 'Building..'
                sh 'cd cppcheck_project && make clean && CXX=gcc make COVERAGE=1'
            }
        }
        stage('Test') {
            steps {
                // Add test commands here
                echo 'Testing..'
                sh 'cd cppcheck_project && CXX=gcc make test COVERAGE=1'
            }
        }
    }
}