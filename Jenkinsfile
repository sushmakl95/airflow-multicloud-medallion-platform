pipeline {
    agent { docker { image 'python:3.11-slim' } }

    environment {
        AIRFLOW_VERSION = '2.9.3'
        PYTHON_VERSION  = '3.11'
        AIRFLOW__CORE__LOAD_EXAMPLES = 'False'
        AIRFLOW__CORE__UNIT_TEST_MODE = 'True'
    }

    options {
        timeout(time: 25, unit: 'MINUTES')
        timestamps()
    }

    stages {
        stage('Lint') {
            steps {
                sh 'pip install -r requirements-dev.txt'
                sh 'ruff check .'
                sh 'black --check dags plugins include src tests'
                sh 'yamllint .'
            }
        }

        stage('Airflow tests') {
            steps {
                sh '''
                    pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
                    pip install -r requirements-dev.txt
                    airflow db migrate
                    pytest tests/ -v --junitxml=reports/junit.xml
                '''
            }
            post {
                always { junit 'reports/junit.xml' }
            }
        }
    }
}
