If you have Docker installed on your local machine, you can use the same Docker Image to compile a draft of your paper locally. In the example below, the paper.md file is in the paper directory. Upon successful execution of the command, the paper.pdf file will be created in the same location as the paper.md file:

```
docker run --rm --volume $PWD/paper:/data --env JOURNAL=joss openjournals/inara
```
