pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out from Git...'
                // Replace with your repository URL and branch
                git branch: 'main', url: 'https://github.com/jboskovic/cppcheck-master.git'
            }
        }
        stage('Build') {
            steps {
                // Add build commands here
                echo 'Building..'
                sh 'cd cppcheck_project &&  make COVERAGE=1'
            }
        }
        stage('Test') {
            steps {
                echo "Get list of tests..."
                sh 'cd cppcheck_project && make testclasses COVERAGE=1'
                // Add test commands here
                echo 'Testing..'
                sh 'cd cppcheck_project && bash run_list_of_tests.sh all_tests.txt'
            }
        }
        stage("Collecting") {
            steps {
                echo "Get code coverage collection..."
                sh 'cd cppcheck_project && python3 ../coverage_tool/collectData.py --sha 612e3d8052f9083609d5b372518869fbeeb62a3d --branch-name main -j8'
            }
        }
    }
}