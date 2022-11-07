#!/bin/sh

# Package Maven application, index files and run search queries
(cd luceneapp/ && mvn package && java -cp target/luceneapp-1.0-SNAPSHOT.jar com.mycompany.luceneapp.IndexFiles; java -cp target/luceneapp-1.0-SNAPSHOT.jar com.mycompany.luceneapp.SearchFiles)

# Run trec_eval and save results to file
(cd trec_eval-9.0.7/ && ./trec_eval -m all_trec ../results/QRelsCorrectedforTRECeval ../luceneapp/my-results.txt > ../results/trec_eval.txt)
