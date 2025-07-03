"""
Central repository for all prompt templates used by the AI assistant.
"""

from typing import Dict, List, Any
import json

class PromptTemplates:
    """Manages and formats prompts for different AI tasks."""

    def get_intent_classification_prompt(self, message: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Creates the prompt for classifying the user's intent."""
        system_prompt = """
        You are an expert at classifying user intent in a compliance context.
        Classify the message into one of: 'evidence_query', 'compliance_check', 'guidance_request', 'general_query'.
        Extract relevant entities like frameworks, evidence types, or specific requirements.
        
        Return a JSON object with this exact format:
        {"type": "evidence_query|compliance_check|guidance_request|general_query", "confidence": 0.9, "entities": {"frameworks": ["ISO27001"], "evidence_types": ["policies"]}}
        """
        
        user_prompt = f"""
        User message: "{message}"
        
        Business context: {json.dumps(context.get('business_profile', {}), indent=2)}
        
        Recent evidence: {json.dumps(context.get('recent_evidence', []), indent=2)}
        
        Please classify this message and extract relevant entities.
        """
        
        return {'system': system_prompt, 'user': user_prompt}

    def get_evidence_query_prompt(self, message: str, evidence_items: List[Any], context: Dict[str, Any]) -> Dict[str, str]:
        """Creates the prompt for answering evidence-related questions."""
        system_prompt = """
        You are ComplianceGPT, an expert compliance assistant. Analyze the user's evidence query and provide helpful insights based on their collected evidence.
        
        Guidelines:
        - Summarize relevant evidence found
        - Identify gaps in evidence collection
        - Suggest specific next steps
        - Reference compliance frameworks when relevant
        - Be concise but thorough
        - Use a helpful, professional tone
        """
        
        evidence_summary = json.dumps([
            {
                'title': getattr(e, 'evidence_name', 'Unknown'),
                'type': getattr(e, 'evidence_type', 'Unknown'),
                'description': getattr(e, 'description', ''),
                'status': getattr(e, 'status', 'active')
            } for e in evidence_items
        ], indent=2)
        
        business_info = context.get('business_profile', {})
        
        user_prompt = f"""
        User question: "{message}"
        
        Business context:
        - Company: {business_info.get('name', 'Unknown')}
        - Industry: {business_info.get('industry', 'Unknown')}
        - Frameworks: {', '.join(business_info.get('frameworks', []))}
        
        Found evidence ({len(evidence_items)} items):
        {evidence_summary}
        
        Compliance status: {json.dumps(context.get('compliance_status', {}), indent=2)}
        
        Please provide a helpful response addressing their question about this evidence.
        """
        
        return {'system': system_prompt, 'user': user_prompt}

    def get_compliance_check_prompt(self, message: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Creates the prompt for compliance status checks."""
        system_prompt = """
        You are ComplianceGPT, a compliance expert. Provide a comprehensive compliance status overview based on the user's current state.
        
        Guidelines:
        - Assess overall compliance readiness
        - Highlight strengths and weaknesses
        - Provide specific recommendations
        - Reference industry standards and frameworks
        - Include actionable next steps
        - Use clear, professional language
        """
        
        business_info = context.get('business_profile', {})
        compliance_status = context.get('compliance_status', {})
        recent_evidence = context.get('recent_evidence', [])
        
        user_prompt = f"""
        User question: "{message}"
        
        Business profile:
        - Company: {business_info.get('name', 'Unknown')}
        - Industry: {business_info.get('industry', 'Unknown')}
        - Target frameworks: {', '.join(business_info.get('frameworks', []))}
        
        Current compliance scores:
        {json.dumps(compliance_status, indent=2)}
        
        Recent evidence activity ({len(recent_evidence)} items):
        {json.dumps(recent_evidence, indent=2)}
        
        Please provide a comprehensive compliance status assessment and recommendations.
        """
        
        return {'system': system_prompt, 'user': user_prompt}

    def get_guidance_request_prompt(self, message: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Creates the prompt for providing compliance guidance."""
        system_prompt = """
        You are ComplianceGPT, a knowledgeable compliance consultant. Provide expert guidance and recommendations based on the user's specific needs.
        
        Guidelines:
        - Offer practical, actionable advice
        - Reference relevant standards and best practices
        - Consider the user's business context and industry
        - Provide step-by-step guidance when appropriate
        - Include relevant resources or references
        - Maintain a helpful, consultative tone
        """
        
        business_info = context.get('business_profile', {})
        
        user_prompt = f"""
        User request: "{message}"
        
        Business context:
        - Company: {business_info.get('name', 'Unknown')}
        - Industry: {business_info.get('industry', 'Unknown')}
        - Frameworks: {', '.join(business_info.get('frameworks', []))}
        
        Current compliance status: {json.dumps(context.get('compliance_status', {}), indent=2)}
        
        Please provide expert guidance tailored to their specific situation and requirements.
        """
        
        return {'system': system_prompt, 'user': user_prompt}

    def get_general_query_prompt(self, message: str, history: List[Dict], context: Dict[str, Any]) -> Dict[str, str]:
        """Creates the prompt for handling general questions."""
        system_prompt = """
        You are ComplianceGPT, a friendly and knowledgeable compliance assistant. Answer the user's question considering the conversation history and their business context.
        
        Guidelines:
        - Be helpful and informative
        - Reference previous conversation context when relevant
        - Provide compliance-focused insights when possible
        - Ask clarifying questions if needed
        - Maintain a professional but approachable tone
        - Keep responses focused and concise
        """
        
        history_str = "\n".join([
            f"{msg['role'].title()}: {msg['content']}" 
            for msg in history[-5:]  # Only include last 5 messages for context
        ])
        
        business_info = context.get('business_profile', {})
        
        user_prompt = f"""
        Recent conversation history:
        {history_str}
        
        User's new message: "{message}"
        
        Business context:
        - Company: {business_info.get('name', 'Unknown')}
        - Industry: {business_info.get('industry', 'Unknown')}
        - Frameworks: {', '.join(business_info.get('frameworks', []))}
        
        Please provide a helpful response that considers the conversation context and their compliance needs.
        """
        
        return {'system': system_prompt, 'user': user_prompt}

    def get_evidence_recommendation_prompt(self, framework: str, business_context: Dict[str, Any]) -> Dict[str, str]:
        """Creates prompts for recommending evidence collection."""
        system_prompt = """
        You are ComplianceGPT, an expert in compliance frameworks. Recommend specific evidence items to collect based on the framework and business context.
        
        Guidelines:
        - Provide specific, actionable recommendations
        - Prioritize by importance and feasibility
        - Consider the business industry and size
        - Include automation opportunities where possible
        - Explain the compliance value of each item
        """
        
        user_prompt = f"""
        Framework: {framework}
        
        Business context:
        {json.dumps(business_context, indent=2)}
        
        Please recommend the top 10 most important evidence items to collect for this framework, prioritized by compliance impact and ease of collection.
        """
        
        return {'system': system_prompt, 'user': user_prompt}

    # Assessment-specific prompt templates for Phase 2.2 integration

    def get_assessment_help_prompt(
        self,
        question_text: str,
        framework_id: str,
        section_id: str = None,
        business_context: Dict[str, Any] = None,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """Creates prompts for assessment question help."""

        system_prompt = f"""You are an expert compliance consultant specializing in {framework_id}.
        Provide clear, actionable guidance for assessment questions.

        Your response should be:
        - Specific to the framework and business context
        - Practical and implementable
        - Include relevant examples when helpful
        - Highlight key considerations and potential pitfalls

        Format your response as JSON with these keys:
        - guidance: Main guidance text
        - confidence_score: Float between 0.0-1.0
        - related_topics: Array of related topics
        - follow_up_suggestions: Array of follow-up questions
        - source_references: Array of relevant documentation
        """

        business_info = business_context or {}
        user_info = user_context or {}

        user_prompt = f"""
        Assessment Question: "{question_text}"

        Framework: {framework_id}
        {f"Section: {section_id}" if section_id else ""}

        Business Context:
        - Company: {business_info.get('name', 'Unknown')}
        - Industry: {business_info.get('industry', 'Unknown')}
        - Size: {business_info.get('employee_count', 'Unknown')} employees
        - Frameworks: {', '.join(business_info.get('frameworks', []))}

        User Context:
        {user_info}

        Please provide comprehensive guidance for answering this assessment question.
        """

        return {'system': system_prompt, 'user': user_prompt}

    def get_assessment_followup_prompt(
        self,
        current_answers: Dict[str, Any],
        framework_id: str,
        business_context: Dict[str, Any] = None,
        assessment_context: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """Creates prompts for generating assessment follow-up questions."""

        system_prompt = f"""You are an expert compliance consultant for {framework_id}.
        Based on the user's current assessment responses, generate intelligent follow-up questions
        that will help complete their compliance assessment.

        Your follow-up questions should:
        - Build on their existing answers
        - Identify gaps or areas needing clarification
        - Be specific to their business context
        - Help prioritize next steps

        Format your response as JSON with these keys:
        - follow_up_questions: Array of specific questions
        - recommendations: Array of immediate recommendations
        - confidence_score: Float between 0.0-1.0
        """

        business_info = business_context or {}
        assessment_info = assessment_context or {}

        user_prompt = f"""
        Current Assessment Responses:
        {current_answers}

        Framework: {framework_id}

        Business Context:
        - Company: {business_info.get('name', 'Unknown')}
        - Industry: {business_info.get('industry', 'Unknown')}
        - Size: {business_info.get('employee_count', 'Unknown')} employees

        Assessment Context:
        - Type: {assessment_info.get('assessment_type', 'general')}
        - Progress: {assessment_info.get('progress', 'unknown')}

        Based on these responses, what follow-up questions should we ask to complete the assessment?
        """

        return {'system': system_prompt, 'user': user_prompt}

    def get_assessment_analysis_prompt(
        self,
        assessment_results: Dict[str, Any],
        framework_id: str,
        business_context: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """Creates prompts for comprehensive assessment analysis."""

        system_prompt = f"""You are an expert compliance analyst specializing in {framework_id}.
        Analyze the completed assessment results to identify gaps, risks, and provide detailed insights.

        Your analysis should include:
        - Specific compliance gaps with severity levels
        - Risk assessment based on current state
        - Evidence requirements for each gap
        - Prioritized recommendations
        - Implementation insights

        Format your response as JSON with these keys:
        - gaps: Array of gap objects with id, title, description, severity, category
        - recommendations: Array of recommendation objects with id, title, description, priority, effort_estimate, impact_score
        - risk_assessment: Object with level and description
        - compliance_insights: Object with summary and key_findings
        - evidence_requirements: Array of evidence requirement objects
        """

        business_info = business_context or {}

        user_prompt = f"""
        Assessment Results:
        {assessment_results}

        Framework: {framework_id}

        Business Context:
        - Company: {business_info.get('name', 'Unknown')}
        - Industry: {business_info.get('industry', 'Unknown')}
        - Size: {business_info.get('employee_count', 'Unknown')} employees
        - Current Frameworks: {', '.join(business_info.get('frameworks', []))}

        Please provide a comprehensive analysis of these assessment results, identifying gaps and providing actionable recommendations.
        """

        return {'system': system_prompt, 'user': user_prompt}

    def get_assessment_recommendations_prompt(
        self,
        gaps: List[Dict[str, Any]],
        business_profile: Dict[str, Any],
        framework_id: str,
        existing_policies: List[str] = None,
        industry_context: str = None,
        timeline_preferences: str = "standard"
    ) -> Dict[str, str]:
        """Creates prompts for generating personalized implementation recommendations."""

        system_prompt = f"""You are an expert compliance implementation consultant for {framework_id}.
        Based on identified gaps and business context, create a detailed implementation plan with personalized recommendations.

        Your recommendations should:
        - Address specific gaps identified
        - Consider business size, industry, and resources
        - Provide realistic timelines and effort estimates
        - Include specific implementation steps
        - Prioritize based on risk and impact

        Format your response as JSON with these keys:
        - recommendations: Array of detailed recommendation objects
        - implementation_plan: Object with phases, timeline, and resource requirements
        - success_metrics: Array of measurable success criteria
        """

        user_prompt = f"""
        Identified Gaps:
        {gaps}

        Framework: {framework_id}

        Business Profile:
        - Company: {business_profile.get('name', 'Unknown')}
        - Industry: {business_profile.get('industry', 'Unknown')}
        - Size: {business_profile.get('employee_count', 'Unknown')} employees
        - Budget Range: {business_profile.get('budget_range', 'Unknown')}

        Existing Policies: {existing_policies or 'None specified'}
        Industry Context: {industry_context or 'General'}
        Timeline Preference: {timeline_preferences}

        Please provide detailed, personalized recommendations with a practical implementation plan.
        """

        return {'system': system_prompt, 'user': user_prompt}
    
    def get_main_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """Creates the main prompt for general AI responses."""
        business_info = context.get('business_profile', {})
        recent_evidence = context.get('recent_evidence', [])
        
        return f"""You are ComplianceGPT, an expert AI compliance assistant. You help organizations understand and implement compliance requirements across various frameworks.

Business Context:
- Company: {business_info.get('company_name', 'Unknown')}
- Industry: {business_info.get('industry', 'Unknown')}
- Employee Count: {business_info.get('employee_count', 'Unknown')}
- Current Frameworks: {', '.join(business_info.get('existing_framew', []))}
- Evidence Collected: {len(recent_evidence)} items

User Message: "{message}"

Please provide a comprehensive, helpful response that:
1. Addresses the user's specific question or need
2. Considers their business context and industry
3. Provides actionable guidance and next steps
4. References relevant compliance frameworks when appropriate
5. Maintains a professional, consultative tone

If you need clarification on any aspect of their request, feel free to ask follow-up questions."""

    def get_context_aware_recommendation_prompt(
        self,
        framework: str,
        business_context: Dict[str, Any],
        maturity_analysis: Dict[str, Any],
        gaps_analysis: Dict[str, Any]
    ) -> Dict[str, str]:
        """Creates enhanced prompts for context-aware recommendations."""

        system_prompt = f"""You are an expert compliance consultant specializing in {framework}.
        Generate intelligent, context-aware evidence collection recommendations that consider:

        1. Organization's specific business context and industry
        2. Current compliance maturity and capabilities
        3. Existing evidence gaps and priorities
        4. Resource constraints and practical implementation
        5. Automation opportunities and efficiency gains
        6. Risk-based prioritization

        Provide recommendations that are:
        - Specific and actionable
        - Prioritized by business impact and feasibility
        - Tailored to organizational maturity level
        - Include automation opportunities where applicable
        - Consider industry-specific requirements

        Return recommendations as a JSON array with detailed structure including:
        - Control mapping and references
        - Implementation steps and guidance
        - Effort estimates and timelines
        - Automation potential and tools
        - Business justification and ROI
        """

        user_prompt = f"""
        Generate context-aware recommendations for {framework} compliance.

        Business Profile:
        - Company: {business_context.get('company_name', 'Unknown')}
        - Industry: {business_context.get('industry', 'Unknown')}
        - Size: {business_context.get('employee_count', 0)} employees
        - Maturity Level: {maturity_analysis.get('maturity_level', 'Basic')}
        - Maturity Score: {maturity_analysis.get('maturity_score', 40)}/100

        Current Compliance Status:
        - Completion: {gaps_analysis.get('completion_percentage', 0)}%
        - Evidence Items: {gaps_analysis.get('evidence_collected', 0)}
        - Critical Gaps: {len(gaps_analysis.get('critical_gaps', []))}
        - Risk Level: {gaps_analysis.get('risk_level', 'Medium')}

        Generate 8-12 prioritized recommendations that address critical gaps while
        considering organizational capacity and maturity level.
        """

        return {'system': system_prompt, 'user': user_prompt}

    def get_workflow_generation_prompt(
        self,
        framework: str,
        control_id: str,
        business_context: Dict[str, Any],
        workflow_type: str
    ) -> Dict[str, str]:
        """Creates prompts for intelligent workflow generation."""

        system_prompt = f"""You are an expert compliance process designer specializing in {framework}.
        Generate comprehensive, step-by-step evidence collection workflows that are:

        1. Tailored to the organization's size and maturity
        2. Practical and implementable with available resources
        3. Include both manual and automated approaches
        4. Provide realistic time estimates and dependencies
        5. Include quality checkpoints and validation criteria
        6. Consider industry-specific requirements
        7. Include role assignments and responsibilities

        Structure the workflow with clear phases, detailed steps, and practical guidance.
        Include automation opportunities and tool recommendations where applicable.
        """

        control_context = f" for control {control_id}" if control_id else ""

        user_prompt = f"""
        Generate a {workflow_type} evidence collection workflow for {framework}{control_context}.

        Organization Context:
        - Company: {business_context.get('company_name', 'Unknown')}
        - Industry: {business_context.get('industry', 'Unknown')}
        - Size: {business_context.get('employee_count', 0)} employees
        - Organization Type: {self._categorize_org_size(business_context.get('employee_count', 0))}

        Requirements:
        - Create 3-5 logical phases with 2-4 steps each
        - Include specific deliverables and validation criteria
        - Provide realistic effort estimates
        - Consider automation opportunities
        - Include role assignments and dependencies
        - Address potential challenges and mitigation strategies

        Generate a comprehensive workflow that can be immediately implemented.
        """

        return {'system': system_prompt, 'user': user_prompt}

    def get_policy_generation_prompt(
        self,
        framework: str,
        policy_type: str,
        business_context: Dict[str, Any],
        customization_options: Dict[str, Any]
    ) -> Dict[str, str]:
        """Creates prompts for customized policy generation."""

        system_prompt = f"""You are an expert compliance policy writer specializing in {framework}.
        Generate comprehensive, business-specific policies that are:

        1. Fully compliant with {framework} requirements
        2. Tailored to the organization's industry and size
        3. Written in clear, professional language
        4. Include specific procedures and controls
        5. Address industry-specific risks and requirements
        6. Practical and implementable
        7. Include roles, responsibilities, and governance

        The policy should be comprehensive yet practical, addressing all relevant
        compliance requirements while being tailored to the organization's context.
        """

        industry = business_context.get('industry', 'Unknown')
        org_size = self._categorize_org_size(business_context.get('employee_count', 0))

        user_prompt = f"""
        Generate a comprehensive {policy_type} policy for {framework} compliance.

        Organization Profile:
        - Company: {business_context.get('company_name', 'Organization')}
        - Industry: {industry}
        - Size: {business_context.get('employee_count', 0)} employees ({org_size})
        - Geographic Scope: {customization_options.get('geographic_scope', 'Single location')}

        Customization Requirements:
        - Tone: {customization_options.get('tone', 'Professional')}
        - Detail Level: {customization_options.get('detail_level', 'Standard')}
        - Industry Focus: {industry}

        Generate a policy with:
        - 5-8 comprehensive sections
        - Detailed procedures and controls
        - Clear roles and responsibilities
        - Compliance requirements mapping
        - Implementation guidance
        - Industry-specific considerations

        Ensure the policy is immediately usable and addresses all {framework} requirements.
        """

        return {'system': system_prompt, 'user': user_prompt}

    def _categorize_org_size(self, employee_count: int) -> str:
        """Helper method to categorize organization size."""
        if employee_count >= 1000:
            return "enterprise"
        elif employee_count >= 100:
            return "medium"
        elif employee_count >= 10:
            return "small"
        else:
            return "micro"