import leetcode
import leetcode_secrets
from slugify import slugify
from dotenv import load_dotenv
from pymongo import MongoClient
import os

class LeetcodeInst:
    def __init__(self):
        leetcode_session = leetcode_secrets.LEETCODE_SESSION
        csrf_token = leetcode_secrets.CSRF_TOKEN

        configuration = leetcode.Configuration()

        configuration.api_key["x-csrftoken"] = csrf_token
        configuration.api_key["csrftoken"] = csrf_token
        configuration.api_key["LEETCODE_SESSION"] = leetcode_session
        configuration.api_key["Referer"] = "https://leetcode.com"
        configuration.debug = False

        self.api_instance = leetcode.DefaultApi(leetcode.ApiClient(configuration))

    def get_progress_weekly(self):
        return self.get_lc_cache_sum()
    
    def get_problem_list(self):
        raw_problems = self.get_problems_raw()
        problem_list = []
        for problem_data in raw_problems:
            problem_data.status
            name = problem_data.title
            url = self.get_problem_url(name)
            difficulty = problem_data.difficulty
            tags = [tag.name for tag in problem_data.topic_tags]
            problem_list.append((name, url, difficulty, tags))

        return problem_list
    
    def get_problems_raw(self):
        graphql_request = leetcode.GraphqlQuery(
            query="""
            query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
              problemsetQuestionList: questionList(
                categorySlug: $categorySlug
                limit: $limit
                skip: $skip
                filters: $filters
              ) {
                totalNum
                questions: data {
                    questionId
                    questionFrontendId
                    boundTopicId
                    title
                    frequency
                    freqBar
                    content
                    translatedTitle
                    isPaidOnly
                    difficulty
                    likes
                    dislikes
                    isLiked
                    isFavor
                    similarQuestions
                    contributors {
                      username
                      profileUrl
                      avatarUrl
                      __typename
                    }
                    langToValidPlayground
                    topicTags {
                      name
                      slug
                      translatedName
                      __typename
                    }
                    companyTagStats
                    codeSnippets {
                      lang
                      langSlug
                      code
                      __typename
                    }
                    stats
                    acRate
                    codeDefinition
                    hints
                    solution {
                      id
                      canSeeDetail
                      __typename
                    }
                    hasSolution
                    hasVideoSolution
                    status
                    sampleTestCase
                    enableRunCode
                    metaData
                    translatedContent
                    judgerAvailable
                    judgeType
                    mysqlSchemas
                    enableTestMode
                    envInfo
                    __typename
                }
              }
            }
            """,
            variables=leetcode.GraphqlQueryProblemsetQuestionListVariables(
                category_slug="algorithms",
                limit=10,
                skip=3,
                filters=leetcode.GraphqlQueryProblemsetQuestionListVariablesFilterInput(
                    status='NOT_STARTED',
                    premium_only=False,
                ),
            ),
            operation_name="problemsetQuestionList",
        )
        response = self.api_instance.graphql_post(body=graphql_request)
        data = response.data
        question_list = data.problemset_question_list.questions
        return question_list
    
    def problem_is_completed(self, title_slug):
    
        graphql_request = leetcode.GraphqlQuery(
                query="""
                    query getQuestionDetail($titleSlug: String!) {
                    question(titleSlug: $titleSlug) {
                        questionId
                        questionFrontendId
                        boundTopicId
                        title
                        titleSlug
                        frequency
                        freqBar
                        content
                        translatedTitle
                        isPaidOnly
                        difficulty
                        likes
                        dislikes
                        isLiked
                        isFavor
                        similarQuestions
                        contributors {
                        username
                        profileUrl
                        avatarUrl
                        __typename
                        }
                        langToValidPlayground
                        topicTags {
                        name
                        slug
                        translatedName
                        __typename
                        }
                        companyTagStats
                        codeSnippets {
                        lang
                        langSlug
                        code
                        __typename
                        }
                        stats
                        acRate
                        codeDefinition
                        hints
                        solution {
                        id
                        canSeeDetail
                        __typename
                        }
                        hasSolution
                        hasVideoSolution
                        status
                        sampleTestCase
                        enableRunCode
                        metaData
                        translatedContent
                        judgerAvailable
                        judgeType
                        mysqlSchemas
                        enableTestMode
                        envInfo
                        __typename
                    }
                    }
                """,
                variables=leetcode.GraphqlQueryGetQuestionDetailVariables(title_slug=title_slug),
                operation_name="getQuestionDetail",
            )

        response = self.api_instance.graphql_post(body=graphql_request)

        data = response.data

        return data.question.status == 'ac'
    
    def get_problem_url(self, title):
        base_url = "https://leetcode.com/problems/"
        base_url += slugify(title)
        return base_url
    
    def get_lc_cache_sum(self):
        sum = 0
        lc_collection = self.open_collection('lc_cache')
        cached_problems = lc_collection.find()
        for problem in cached_problems:
            if self.check_lc_entry(problem['title']):
                sum += 1
        return sum

    def check_lc_entry(self, title):
        title_slug = slugify(title)
        return self.problem_is_completed(title_slug)

    def open_collection(self, collection_name):
        load_dotenv()
        MONGODB_URI = os.environ['MONGODB_URI']

        # Connect to your MongoDB cluster:
        client = MongoClient(MONGODB_URI)

        # Select the database you want to use:
        db = client['dashboard']
        collection = db[collection_name]

        return collection

    


def main():
    test_object = LeetcodeInst()

    print(test_object.get_progress_weekly())
   

if __name__=="__main__":
    main()

    
