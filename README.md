# git-log-analytics
Python process to analyze a repo's git log for user activity and hot spots of code

This python script reads a pre-generated git log output text file, creates a CSV file of useful columns that can be use for further analysis, and creates charts showing repo activity. There are lots of existing tools that do this but seem to have been abandoned or require server software to present visualizations of the data. 

It was inspired by Adam Tornhill's [GOTO 2019 Prioritizing Technical Debt as if Time and Money Matters](https://www.youtube.com/watch?v=fl4aZ2KXBsQ) talk.

## Pre-reqs
* git command line installed
* repo for analysis is located in a parent directory (sibiling to the level of this repo)
* install the project requirements
```
pip install requirements.txt
```
## Usage
Run the process_parent_dir.sh bash script supplying a parent directory of a different repo.

``` bash
# analyze the local cloned elasticsearch repo
. process_parent_dir.sh  elasticsearch
```

The script will:
* navigate to the parent directory repo
* pull the latest code
* create a formated git log text file 
* run the python script to analyze the log output and create the following in the output/ folder:
    * git_analysis_result.csv - CSV of analyzed file commit info
    * PNGs of analysis charts
    * git_log.csv - CSV of commit log info
    * results.html - Local HTML file to display the charts and hotspot info. 


## Samples
See the [samples/](sample/README.md) folder for sample run on the elasticsearch repo. 



```
🔥 Hotspots 
Commits  Comp.   Age    Score  File
  479   328395     7    100.0  server/src/test/java/org/elasticsearch/index/engine/InternalEngineTests.java
  478   181024     6     55.0  server/src/main/java/org/elasticsearch/index/shard/IndexShard.java
  357   208313     1     47.3  server/src/test/java/org/elasticsearch/index/shard/IndexShardTests.java
  422   164637     0     44.2  server/src/main/java/org/elasticsearch/repositories/blobstore/BlobStoreRepository.java
  334   175359     2     37.2  server/src/main/java/org/elasticsearch/snapshots/SnapshotsService.java
  265   213786    20     36.0  client/rest-high-level/src/test/java/org/elasticsearch/client/documentation/MlClientDocumentationIT.java
  387   140061     7     34.5  server/src/main/java/org/elasticsearch/index/engine/InternalEngine.java
  450   107638    13     30.8  test/framework/src/main/java/org/elasticsearch/test/InternalTestCluster.java
  291   163705    36     30.3  client/rest-high-level/src/test/java/org/elasticsearch/client/MachineLearningIT.java
  389   105875    11     26.2  test/framework/src/main/java/org/elasticsearch/test/ESIntegTestCase.java


```




## Tests
```
>. run_tests.sh  

Generating HTML reports... 
reports/test_results.json_test_unit_analysis.UnitTests.html
reports/test_results.json_test_unit_git_log.UnitTests.html


🗃  Test Results:


📋 test_unit_git_log.UnitTests:
   Status  | Test
   ---------------------------------------------------
   ✅ pass  | test_process__given_file_in_four_dir__then_dirs_correct                         
   ✅ pass  | test_process__given_file_in_one_dir__then_dir_1_correct                         
   ✅ pass  | test_process__given_files_with_different_dirs__then_dirs_correct                
   ✅ pass  | test_process__given_insertion_is_dash__then_churn_set_to_two                    
   ✅ pass  | test_process__given_timezone_is_gmt__then_results_are_correct                   
   ✅ pass  | test_process__given_two_commits_three_files__then_three_lines_created           


📋 test_unit_analysis.UnitTests:
   Status  | Test
   ---------------------------------------------------
   ✅ fail  | test_calculate_file_commits__given_simple_test_data__then_correct_data_returned 
   ✅ pass  | test_calculate_file_complexity__given_input_dir_of_files__files_scores_returned 
   ✅ pass  | test_determine_hotspot_data__given_simple_data__then_correct_data_returned      
   ✅ fail  | test_get_commit_age__given_simple_test_data__then_correct_data_returned         
   ✅ pass  | test_get_top_hotspots__given_short_list__then_top_3_returned                    
   ✅ pass  | test_is_code_file__given_image__then_return_false                               
   ✅ pass  | test_is_code_file__given_lock__then_return_false                                
   ✅ pass  | test_is_code_file__given_readme__then_return_false                              
   ✅ pass  | test_is_code_file__given_text_file__then_return_true                            
   ✅ fail  | test_read_analytics__given_valid_csv_file__then_df_returned                     

🗂  Total Tests: 16



