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