pipeline {
    agent any

    stages {
        stage('Verify Linux Environment') {
            steps {
                script {
                    echo "Operating System Information:"
                    sh 'uname -a'
                    echo "Distribution Information:"
                    sh 'lsb_release -a 2>/dev/null || cat /etc/*release'
                    echo "Current User:"
                    sh 'whoami'
                    echo "Home Directory:"
                    sh 'echo $HOME'
                }
            }
        }
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