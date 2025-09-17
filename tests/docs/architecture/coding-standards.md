# Coding Standards

## Overview
This document defines the coding standards for the RuleIQ frontend application.

## TypeScript Standards
- Use strict TypeScript configuration
- Always provide type annotations for function parameters and return values
- Avoid using `any` type unless absolutely necessary
- Use interfaces for object shapes
- Use enums for fixed sets of values

## React Standards
- Use functional components with hooks
- Follow React best practices for component composition
- Use proper key props for lists
- Implement proper error boundaries
- Use React.memo for performance optimization where needed

## Code Organization
- Keep files under 500 lines
- One component per file
- Group related functionality in directories
- Use barrel exports for cleaner imports

## Testing Standards
- Write tests for all new features
- Maintain >80% code coverage
- Use React Testing Library for component tests
- Use MSW for API mocking

## Documentation
- Document complex logic with comments
- Use JSDoc for public APIs
- Keep README files updated