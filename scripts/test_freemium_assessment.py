"""
from __future__ import annotations

# Constants


Automated test script for the freemium assessment feature.
Tests the complete flow from lead capture through 5 questions.
"""
import asyncio
import time
import httpx
from datetime import datetime

from tests.test_constants import (
    HTTP_OK
)
BASE_URL = 'http://localhost:8000/api/v1'
TEST_EMAIL = f'test_{int(time.time())}@example.com'
EXPECTED_MIN_QUESTIONS = 5


class FreemiumAssessmentTester:

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.lead_id = None
        self.session_token = None
        self.questions_answered = 0
        self.current_question = None

    async def close(self):
        await self.client.aclose()

    async def test_lead_capture(self) ->bool:
        """Step 1: Capture lead information"""
        print('\n🔹 Step 1: Capturing lead...')
        payload = {'email': TEST_EMAIL, 'first_name': 'Test', 'last_name':
            'User', 'company_name': 'Test Company', 'company_size': '11-50',
            'industry': 'Technology'}
        try:
            response = await self.client.post(f'{BASE_URL}/freemium/leads',
                json=payload)
            if response.status_code in [200, 201]:
                data = response.json()
                self.lead_id = data.get('id')
                print(f'✅ Lead captured successfully: {self.lead_id}')
                print(f'   Email: {TEST_EMAIL}')
                return True
            else:
                print(f'❌ Failed to capture lead: {response.status_code}')
                print(f'   Response: {response.text}')
                return False
        except Exception as e:
            print(f'❌ Error capturing lead: {e}')
            return False

    async def test_start_session(self) ->bool:
        """Step 2: Start assessment session"""
        print('\n🔹 Step 2: Starting assessment session...')
        payload = {'lead_email': TEST_EMAIL, 'business_type': 'technology',
            'company_size': '11-50', 'assessment_type': 'general'}
        try:
            response = await self.client.post(f'{BASE_URL}/freemium/sessions',
                json=payload)
            if response.status_code in [200, 201]:
                data = response.json()
                self.session_token = data.get('session_token')
                first_question = data.get('current_question')
                if first_question:
                    self.current_question = first_question
                    print(f'✅ Session started: {self.session_token}')
                    print(
                        f"   First question: {first_question.get('question_text', 'N/A')[:100]}..."
                        )
                    return True
                else:
                    print('⚠️ Session started but no first question provided')
                    return False
            else:
                print(f'❌ Failed to start session: {response.status_code}')
                print(f'   Response: {response.text}')
                return False
        except Exception as e:
            print(f'❌ Error starting session: {e}')
            return False

    async def test_answer_questions(self) ->bool:
        """Step 3: Answer minimum required questions"""
        print(f'\n🔹 Step 3: Answering {EXPECTED_MIN_QUESTIONS} questions...')
        sample_answers = [
            'We are a technology company focused on SaaS solutions',
            'Yes, we process customer data from EU residents',
            'We have approximately 500 active customers',
            'We currently use basic security measures and are looking to improve'
            , 'Our main compliance concern is GDPR and data protection']
        for i in range(EXPECTED_MIN_QUESTIONS):
            print(f'\n   📝 Question {i + 1}/{EXPECTED_MIN_QUESTIONS}')
            if not self.current_question:
                session_response = await self.client.get(
                    f'{BASE_URL}/freemium/sessions/{self.session_token}')
                if session_response.status_code == HTTP_OK:
                    session_data = session_response.json()
                    self.current_question = session_data.get('current_question'
                        )
                    if not self.current_question:
                        print('   ❌ No question available')
                        return False
            question_text = self.current_question.get('question_text',
                'Unknown question')
            print(f'   Q: {question_text[:150]}...')
            answer_payload = {'question_id': self.current_question.get('id',
                f'q_{i + 1}'), 'answer': sample_answers[i % len(
                sample_answers)], 'answer_confidence': 'high',
                'time_spent_seconds': 10}
            try:
                answer_response = await self.client.post(
                    f'{BASE_URL}/freemium/sessions/{self.session_token}/answers'
                    , json=answer_payload)
                if answer_response.status_code == HTTP_OK:
                    answer_data = answer_response.json()
                    self.questions_answered += 1
                    print('   ✅ Answer submitted successfully')
                    next_question = answer_data.get('next_question')
                    if next_question:
                        self.current_question = next_question
                        print('   → Next question ready')
                    else:
                        self.current_question = None
                        if i < EXPECTED_MIN_QUESTIONS - 1:
                            print(
                                f'   ⚠️ No next question provided (answered: {self.questions_answered})'
                                )
                else:
                    print(
                        f'   ❌ Failed to submit answer: {answer_response.status_code}'
                        )
                    print(f'      Response: {answer_response.text}')
                    return False
            except Exception as e:
                print(f'   ❌ Error submitting answer: {e}')
                return False
            await asyncio.sleep(0.5)
        print(
            f'\n   ✅ Answered {self.questions_answered} questions successfully'
            )
        return self.questions_answered >= EXPECTED_MIN_QUESTIONS

    async def test_get_results(self) ->bool:
        """Step 4: Get assessment results"""
        print('\n🔹 Step 4: Getting assessment results...')
        try:
            response = await self.client.get(
                f'{BASE_URL}/freemium/sessions/{self.session_token}/results')
            if response.status_code == HTTP_OK:
                results = response.json()
                print('✅ Results generated successfully!')
                if 'compliance_score' in results:
                    print(f"   Compliance Score: {results['compliance_score']}"
                        )
                if 'risk_level' in results:
                    print(f"   Risk Level: {results['risk_level']}")
                if 'recommendations' in results:
                    recs = results['recommendations']
                    print(
                        f"   Recommendations: {len(recs) if isinstance(recs, list) else 'Available'}"
                        )
                return True
            else:
                print(f'❌ Failed to get results: {response.status_code}')
                print(f'   Response: {response.text}')
                return False
        except Exception as e:
            print(f'❌ Error getting results: {e}')
            return False

    async def run_full_test(self):
        """Run the complete test suite"""
        print('=' * 60)
        print('🧪 FREEMIUM ASSESSMENT AUTOMATED TEST')
        print('=' * 60)
        print(f'Timestamp: {datetime.now()}')
        print(f'Test Email: {TEST_EMAIL}')
        print(f'API Endpoint: {BASE_URL}')
        results = {'lead_capture': False, 'session_start': False,
            'questions_answered': False, 'results_generated': False}
        try:
            results['lead_capture'] = await self.test_lead_capture()
            if not results['lead_capture']:
                print('\n⛔ Stopping test - lead capture failed')
                return results
            results['session_start'] = await self.test_start_session()
            if not results['session_start']:
                print('\n⛔ Stopping test - session start failed')
                return results
            results['questions_answered'] = await self.test_answer_questions()
            if not results['questions_answered']:
                print('\n⛔ Stopping test - failed to answer minimum questions')
                return results
            results['results_generated'] = await self.test_get_results()
        except Exception as e:
            print(f'\n❌ Unexpected error during test: {e}')
        print('\n' + '=' * 60)
        print('📊 TEST SUMMARY')
        print('=' * 60)
        all_passed = all(results.values())
        for test_name, passed in results.items():
            status = '✅ PASSED' if passed else '❌ FAILED'
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        print('\n' + '=' * 60)
        if all_passed:
            print('🎉 ALL TESTS PASSED - Assessment working correctly!')
        else:
            print('⚠️ SOME TESTS FAILED - Investigation needed')
        print('=' * 60)
        return results


async def main():
    tester = FreemiumAssessmentTester()
    try:
        results = await tester.run_full_test()
        return 0 if all(results.values()) else 1
    finally:
        await tester.close()


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    exit(exit_code)
