pipeline {
  agent { docker { image 'python:3.7.2' } }
  stages {
    stage('build') {
      steps {
        sh 'pip install -r devrequirements.txt --user'
      }
    }
    stage('test') {
      steps {
        sh 'python unittest discover'
      }
    }
  }
}
