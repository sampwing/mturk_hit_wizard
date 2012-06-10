from boto.mturk.connection import MTurkConnection

from boto.mturk.question import (
    QuestionForm,
    Question,
    QuestionContent,
    FreeTextAnswer,
    AnswerSpecification,
    ExternalQuestion
)

ACCESS_ID ='AKIAIJ6MLX6LGQTP3MRA'
SECRET_KEY = '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'
HOST = 'mechanicalturk.sandbox.amazonaws.com'

class MTurk(object):
    def __init__(self):
        self.mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                                   aws_secret_access_key=SECRET_KEY,
                                   host=HOST)
    def balance(self):
        return self.mtc.get_account_balance()

    def create_question(self, id, title):
        content = QuestionContent()
        content.append_field('Title', title)
        text = FreeTextAnswer()
        return Question(identifier=id, content=content, answer_spec=AnswerSpecification(text))

    def create_hit(self, title, description=''):
        question_form = QuestionForm()
        question_form.append(self.create_question(id='1', title='Comments'))
        question_form.append(self.create_question(id='2', title='More Comments'))
        self.mtc.create_hit(questions=question_form, max_assignments=1, title=title, description=description,
            duration=60*5, reward=0.01)

    def external(self):
        q = ExternalQuestion(external_url="http://mturk-hit-wizard.herokuapp.com/view/2", frame_height=800)
        #conn = MTurkConnection(host=HOST)
        keywords=['boto', 'test', 'doctest']
        create_hit_rs = self.mtc.create_hit(question=q, lifetime=60*65,max_assignments=2,title="Boto External Question Test", keywords=keywords,reward = 0.05, duration=60*6,approval_delay=60*60, annotation='An annotation from boto external question test', response_groups=['Minimal','HITDetail','HITQuestion','HITAssignmentSummary',])
        assert(create_hit_rs.status == True)


mturk = MTurk()
print mturk.balance()

#print mturk.create_hit(title="Comment Form", description="Free form for entering comments")
mturk.external()
#http://www.toforge.com/2011/04/boto-mturk-tutorial-create-hits/
