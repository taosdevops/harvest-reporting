pipeline {
  agent { docker { image 'python:3-alpine' } }
  // agent { docker { image 'python:3.7.2' } }
  // agent { dockerfile: true }
  stages {
    // agent { docker { image 'python:3-alpine' } }
    stage('test') {
      steps {
          withEnv(["HOME=${env.WORKSPACE}"]) {
              sh 'pip install --user -r requirements.txt'
              sh 'python WebChecker.py'
              sh 'python unittest discover'
          }
      }
        // sh 'chmod +x scripts/build.sh'
        // sh 'scripts/build.sh'
      // }
    }
    // stage('test') {
    //   steps {
        
    //   }
    // }
  }
}
