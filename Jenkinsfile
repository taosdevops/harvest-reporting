pipeline {
  agent { docker { image 'python:3.7.2' } }
  stages {
    stage('build') {
      steps {
        sh 'chmod +x scripts/build.sh'
        sh 'scripts/build.sh'
      }
    }
    stage('test') {
      steps {
        sh 'python unittest discover'
      }
    }
  }
}
