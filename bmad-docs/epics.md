# clan-core - Epic Breakdown

**Author:** Lord
**Date:** 2025-11-14
**Project Level:** [Please specify: MVP, Growth, Enterprise, etc.]
**Target Scale:** [Please specify: Users, Transactions, etc.]

---

## Overview

This document provides the complete epic and story breakdown for clan-core, decomposing the requirements from the [PRD](./PRD.md) into implementable stories.

**Living Document Notice:** This is the initial version. It will be updated after UX Design and Architecture workflows add interaction and technical details to stories.

## Epic Structure Summary

The epic breakdown organizes 50 functional requirements into 10 cohesive epics that enable incremental value delivery and sustainable infrastructure management:

**Epic 1: Foundation & Development Environment**
Essential infrastructure setup including development shell, branch management, and core tooling needed to build and test all other features.

**Epic 2: Installation & Bootstrap**
Single-command installation workflow enabling users to quickly start using Arda without manual configuration complexity.

**Epic 3: Machine Lifecycle Management**
Complete machine lifecycle from creation to deployment, enabling users to manage NixOS infrastructure declaratively.

**Epic 4: Service/Feature/Role Architecture**
The core differentiator of Arda - hierarchical organization system enabling composable, reusable infrastructure components.

**Epic 5: Template System**
Built-in templates and customization system for common patterns (disk layouts, service configurations).

**Epic 6: Secret Management (Priority Focus)**
Critical security infrastructure with sops-nix integration, age key distribution, and encrypted secret storage.

**Epic 7: Configuration Abstraction Layer**
The core library (arda-core.lib.arda) that abstracts Nix complexity and generates configurations automatically.

**Epic 8: Update & Maintenance Framework**
Flake-based update workflow enabling conflict-free updates and decade-scale sustainability.

**Epic 9: Status & Diagnostics**
System health monitoring, drift detection, and clear error messaging for operational excellence.

**Epic 10: Deployment & Operations**
Multi-machine deployment capabilities with idempotent operations and comprehensive logging.

This structure prioritizes the foundation-first approach, with Epic 6 (Secret Management) receiving priority focus due to its criticality and complexity.

---

## Functional Requirements Inventory

**FR Inventory for clan-core / Arda:**

**User Account & Access:**

- FR1: Users can generate age keys for encrypting and decrypting secrets across all managed machines
- FR2: Users can bootstrap a new Arda installation via single `nix run` command without manual configuration
- FR3: Users can create GitHub repository for their Arda configuration with proper template structure

**Machine Lifecycle Management:**

- FR4: Users can create machine configurations via `arda machine create <hostname>` command
- FR5: Users can deploy machines to target hosts via `arda machines install <hostname>` command
- FR6: Users can view all managed machines and their current configuration status
- FR7: Users can remove machines from management while preserving historical configuration data

**Service/Feature/Role Architecture:**

- FR8: Users can define individual Services as atomic, tested building blocks in services/ directory
- FR9: Users can compose Features as combinations of related Services in features/ directory
- FR10: Users can define Roles as machine-level assignments combining multiple Features in roles/ directory
- FR11: Users can assign Roles to machines via declarative arda.nix configuration
- FR12: Users can create custom roles by combining existing features without duplicating service definitions
- FR13: Users can preview role composition before applying to machines

**Template System:**

- FR14: Users can apply built-in templates to machines via `arda templates apply <template> <machine>` command
- FR15: Users can customize template variables to match their specific requirements
- FR16: Users can create custom templates for recurring patterns (disk layouts, service configs)
- FR17: Users can list available templates and view documentation for each template

**Secret Management:**

- FR18: All secrets are automatically encrypted via sops-nix before storage in repository
- FR19: Age keys are distributed securely to authorized machines based on role assignments
- FR20: Users can rotate secrets without manual re-encryption across all machines
- FR21: Machine-specific secrets are accessible only to authorized roles
- FR22: Secret operations produce no plaintext output in CLI or logs

**Configuration Generation & Abstraction:**

- FR23: Users can declare machine configurations in simple arda.nix without understanding Nix module internals
- FR24: arda-core.lib.arda library automatically generates nixosConfigurations from directory structure
- FR25: Users can override default configurations per machine via directory structure conventions
- FR26: Configuration changes are validated before deployment to prevent misconfigurations

**Abstraction Layer & Compatibility:**

- FR27: Users can migrate existing clan-style configurations with minimal modifications
- FR28: arda-core provides compatibility layer for direct service definitions during transition
- FR29: Users can define custom services following established patterns and best practices
- FR30: The abstraction layer handles all complexity of Nix module composition transparently

**Update & Maintenance:**

- FR31: Users can update Arda core via `nix flake update` without merge conflicts in user configurations
- FR32: User customizations remain intact through core framework updates
- FR33: Users can rollback to previous Arda core version if update causes issues
- FR34: Update workflow validates configuration compatibility before applying changes

**Development Environment:**

- FR35: Users can access development shell via `nix develop` with arda-cli pre-configured
- FR36: Users can test changes in isolation before committing to main configuration
- FR37: Branch management helpers support clan-core reference and arda-v1 development workflows
- FR38: Users can manage flake.lock state and resolve dependency conflicts

**Status & Diagnostics:**

- FR39: Users can view status of all machines and pending changes
- FR40: Configuration drift is detected and reported with actionable recommendations
- FR41: Failed deployments are automatically rolled back to last known good state
- FR42: Clear error messages provide specific recovery paths for common issues

**Directory Structure Management:**

- FR43: Machines are organized in machines/<hostname>/ directory structure
- FR44: Services, Features, and Roles have dedicated directory structures (services/, features/, roles/)
- FR45: Secrets directory structure is automatically generated with proper sops-nix integration
- FR46: Template library is searchable and categorized by type and use case

**Deployment & Operations:**

- FR47: Users can deploy multiple machines in parallel with progress tracking
- FR48: Deployment operations are idempotent (multiple runs produce same result)
- FR49: Users can preview changes before applying them to production machines
- FR50: All deployment operations log actions for troubleshooting and audit purposes

**Total: 50 Functional Requirements**

---

## FR Coverage Map

**Epic 1: Foundation & Development Environment**

- FR35: Users can access development shell via `nix develop` with arda-cli pre-configured
- FR36: Users can test changes in isolation before committing to main configuration
- FR37: Branch management helpers support clan-core reference and arda-v1 development workflows
- FR38: Users can manage flake.lock state and resolve dependency conflicts

**Epic 2: Installation & Bootstrap**

- FR2: Users can bootstrap a new Arda installation via single `nix run` command without manual configuration
- FR3: Users can create GitHub repository for their Arda configuration with proper template structure

**Epic 3: Machine Lifecycle Management**

- FR4: Users can create machine configurations via `arda machine create <hostname>` command
- FR5: Users can deploy machines to target hosts via `arda machines install <hostname>` command
- FR6: Users can view all managed machines and their current configuration status
- FR7: Users can remove machines from management while preserving historical configuration data
- FR43: Machines are organized in machines/<hostname>/ directory structure

**Epic 4: Service/Feature/Role Architecture**

- FR8: Users can define individual Services as atomic, tested building blocks in services/ directory
- FR9: Users can compose Features as combinations of related Services in features/ directory
- FR10: Users can define Roles as machine-level assignments combining multiple Features in roles/ directory
- FR11: Users can assign Roles to machines via declarative arda.nix configuration
- FR12: Users can create custom roles by combining existing features without duplicating service definitions
- FR13: Users can preview role composition before applying to machines
- FR44: Services, Features, and Roles have dedicated directory structures (services/, features/, roles/)

**Epic 5: Template System**

- FR14: Users can apply built-in templates to machines via `arda templates apply <template> <machine>` command
- FR15: Users can customize template variables to match their specific requirements
- FR16: Users can create custom templates for recurring patterns (disk layouts, service configs)
- FR17: Users can list available templates and view documentation for each template
- FR46: Template library is searchable and categorized by type and use case

**Epic 6: Secret Management (Priority Focus)**

- FR1: Users can generate age keys for encrypting and decrypting secrets across all managed machines
- FR18: All secrets are automatically encrypted via sops-nix before storage in repository
- FR19: Age keys are distributed securely to authorized machines based on role assignments
- FR20: Users can rotate secrets without manual re-encryption across all machines
- FR21: Machine-specific secrets are accessible only to authorized roles
- FR22: Secret operations produce no plaintext output in CLI or logs
- FR45: Secrets directory structure is automatically generated with proper sops-nix integration

**Epic 7: Configuration Abstraction Layer**

- FR23: Users can declare machine configurations in simple arda.nix without understanding Nix module internals
- FR24: arda-core.lib.arda library automatically generates nixosConfigurations from directory structure
- FR25: Users can override default configurations per machine via directory structure conventions
- FR26: Configuration changes are validated before deployment to prevent misconfigurations
- FR27: Users can migrate existing clan-style configurations with minimal modifications
- FR28: arda-core provides compatibility layer for direct service definitions during transition
- FR29: Users can define custom services following established patterns and best practices
- FR30: The abstraction layer handles all complexity of Nix module composition transparently

**Epic 8: Update & Maintenance Framework**

- FR31: Users can update Arda core via `nix flake update` without merge conflicts in user configurations
- FR32: User customizations remain intact through core framework updates
- FR33: Users can rollback to previous Arda core version if update causes issues
- FR34: Update workflow validates configuration compatibility before applying changes

**Epic 9: Status & Diagnostics**

- FR39: Users can view status of all machines and pending changes
- FR40: Configuration drift is detected and reported with actionable recommendations
- FR41: Failed deployments are automatically rolled back to last known good state
- FR42: Clear error messages provide specific recovery paths for common issues

**Epic 10: Deployment & Operations**

- FR47: Users can deploy multiple machines in parallel with progress tracking
- FR48: Deployment operations are idempotent (multiple runs produce same result)
- FR49: Users can preview changes before applying them to production machines
- FR50: All deployment operations log actions for troubleshooting and audit purposes

**Coverage Validation:** ✅ All 50 FRs mapped to epics

---

<!-- Epic breakdown begins -->

## Epic 1: Foundation & Development Environment

Establish the essential development infrastructure needed to build and iterate on all other Arda features. This epic creates the foundation for rapid, testable development.

### Story 1.1: Project Setup and Repository Initialization

As a developer,
I want to initialize the Arda project repository with proper structure and tooling,
So that I can begin building features in an organized, reproducible environment.

**Acceptance Criteria:**

**Given** I have a clean Git repository
**When** I run the initialization process
**Then** the repository contains proper directory structure (src/, tests/, docs/, etc.)

**And** GitHub repository is created with initial commit
**And** Git hooks and pre-commit checks are configured
**And** Development documentation explains the project structure

**Prerequisites:** None - this is the first story

**Technical Notes:**

- Create GitHub repo: <https://github.com/lorddevi/arda-core>
- Initialize with .gitignore for Nix projects and secrets
- Set up branch strategy: main (arda-v1), clan-core (reference)
- Add basic README.md with project overview and development setup

---

### Story 1.2: Development Shell Configuration

As a developer,
I want access to a `nix develop` shell with all necessary tools pre-configured,
So that I can immediately start developing without spending time on environment setup.

**Acceptance Criteria:**

**Given** I enter the project directory
**When** I run `nix develop`
**Then** I have access to Python 3.11+, arda-cli, and all required Nix tools

**And** The shell includes testing tools (pytest, black, flake8)
**And** Development utilities are available (git, gh, direnv)
**And** Shell prompt clearly indicates I'm in the Arda development environment

**Prerequisites:** Story 1.1 completed

**Technical Notes:**

- Configure shell.nix with all Python and Nix dependencies
- Install arda-cli as editable package during development
- Set up PATH so `arda` command works in shell
- Document required tools in README.md development section

---

### Story 1.3: Branch Management Workflow Setup

As a developer,
I want clear branch management conventions for arda-v1 development,
So that I can maintain clean history while comparing against clan-core reference.

**Acceptance Criteria:**

**Given** I need to work on a new feature
**When** I create a feature branch
**Then** the branch follows naming convention (feature/, bugfix/, experiment/)

**And** I can easily compare changes against clan-core branch
**And** Merge strategy is clear and documented
**And** Feature branches can be deleted after merging

**Prerequisites:** Story 1.1 completed

**Technical Notes:**

- Document branch conventions in CONTRIBUTING.md
- Set up git aliases for common operations
- Create branch protection rules for main branch
- Add scripts for comparing against clan-core

---

### Story 1.4: Flake Configuration and Lock Management

As a developer,
I want a properly configured flake.nix with pinned dependencies,
So that builds are reproducible and dependency conflicts are minimized.

**Acceptance Criteria:**

**Given** I have the Arda repository cloned
**When** I run `nix flake update`
**Then** all dependencies are updated and locked consistently

**And** The update process completes without conflicts
**And** Previous versions can be rolled back if needed
**And** Development environment remains stable across updates

**Prerequisites:** Story 1.2 completed

**Technical Notes:**

- Configure flake.nix with proper inputs (nixpkgs, flake-utils)
- Set up automatic flake lock updates
- Document dependency pinning strategy
- Add CI checks for flake validity

---

### Story 1.5: Testing Framework Setup

As a developer,
I want a comprehensive testing framework for validating Arda features,
So that I can ensure each component works correctly before integration.

**Acceptance Criteria:**

**Given** I write new code
**When** I run the test suite
**Then** all tests execute and provide clear pass/fail feedback

**And** Tests cover CLI commands, module generation, and integration workflows
**And** Tests can run in CI/CD pipeline
**And** Test coverage reports are generated

**Prerequisites:** Stories 1.1-1.4 completed

**Technical Notes:**

- Set up pytest for Python testing
- Create test fixtures for Nix environment testing
- Add integration tests for end-to-end workflows
- Configure test coverage reporting

---

## Epic 2: Installation & Bootstrap

Create a seamless installation experience enabling users to quickly start with Arda through a single, automated command.

### Story 2.1: Age Key Generation Setup

As a new Arda user,
I want to generate age encryption keys automatically,
So that I can securely manage secrets across all my machines.

**Acceptance Criteria:**

**Given** I want to start using Arda
**When** I run the installation command
**Then** age keys are generated automatically and securely stored

**And** Keys are protected with proper file permissions (600)
**And** Public key is displayed for verification
**And** Private key is never output to terminal or logs

**Prerequisites:** Epic 1 completed

**Technical Notes:**

- Integrate age-keygen into installation workflow
- Store keys in ~/.config/arda/ directory
- Generate .sops.yaml with public key for encryption
- Document key backup procedures in user guide

---

### Story 2.2: Single Command Installation Workflow

As a new Arda user,
I want to install and initialize Arda with a single `nix run` command,
So that I can get started without complex manual configuration.

**Acceptance Criteria:**

**Given** I have NixOS with flakes enabled
**When** I run `nix run github:lorddevi/arda-core`
**Then** Arda is installed and initialized in my current directory

**And** Initial configuration is generated (arda.nix, flake.nix)
**And** Directory structure is created (machines/, roles/, features/, services/)
**And** Success message confirms installation with next steps
**And** Installation completes in under 1 minute

**Prerequisites:** Story 2.1 completed

**Technical Notes:**

- Create install script that runs arda-cli init
- Use nix flake output for distribution
- Auto-detect if in existing Arda project
- Provide clear error messages for missing prerequisites

---

### Story 2.3: GitHub Repository Template Creation

As a new Arda user,
I want to create a GitHub repository for my configuration,
So that I can version control and share my infrastructure code.

**Acceptance Criteria:**

**Given** I have completed the basic installation
**When** I run the GitHub creation command
**Then** a GitHub repository is created with proper template structure

**And** Repository includes .gitignore, README.md, and initial configuration
**And** Git remote is set to the new repository
**And** Initial commit is pushed with proper commit message
**And** User is given repository URL for further customization

**Prerequisites:** Story 2.2 completed

**Technical Notes:**

- Integrate GitHub CLI (gh) for repository creation
- Use GitHub API to set up repository with template files
- Provide options for public/private repository
- Add repository URL to local configuration

---

## Epic 3: Machine Lifecycle Management

Enable complete machine lifecycle management from creation to deployment, supporting declarative infrastructure.

### Story 3.1: Machine Configuration Creation

As an Arda user,
I want to create machine configurations via `arda machine create <hostname>`,
So that I can define my infrastructure declaratively without manual file creation.

**Acceptance Criteria:**

**Given** I have an Arda project initialized
**When** I run `arda machine create myserver`
**Then** a machine configuration directory is created at machines/myserver/

**And** Default configuration files are generated (hardware.nix, configuration.nix)
**And** Machine is added to arda.nix nixosConfigurations
**And** Directory structure follows Arda conventions
**And** User receives confirmation with next steps

**Prerequisites:** Epic 2 completed

**Technical Notes:**

- Use Nix module system for machine configuration templates
- Auto-generate hardware configuration from nixos-generate-config
- Create default networking and user setup
- Validate hostname format (RFC-compliant)

---

### Story 3.2: Machine Deployment Workflow

As an Arda user,
I want to deploy machines to target hosts via `arda machines install <hostname>`,
So that I can apply my declarative configuration to actual hardware.

**Acceptance Criteria:**

**Given** I have created a machine configuration
**When** I run `arda machines install myserver`
**Then** the configuration is built and deployed to the target host

**And** Deployment progress is shown with clear status updates
**And** Configuration builds successfully without errors
**And** Target host is rebooted into new configuration
**And** Post-deployment verification confirms successful deployment

**Prerequisites:** Story 3.1 completed

**Technical Notes:**

- Integrate with nixos-anywhere for remote deployment
- Handle SSH key-based authentication
- Support both physical and VM deployments
- Implement rollback on deployment failure

---

### Story 3.3: Machine Status Monitoring

As an Arda user,
I want to view all managed machines and their current configuration status,
So that I can track the state of my infrastructure at a glance.

**Acceptance Criteria:**

**Given** I have deployed multiple machines
**When** I run `arda machines list`
**Then** I see a table showing all machines with their status

**And** Each machine shows hostname, configuration version, and last deployment time
**And** Status indicators show active, inactive, or error states
**And** Command completes in under 5 seconds
**And** Output is color-coded for quick status recognition

**Prerequisites:** Story 3.2 completed

**Technical Notes:**

- Cache machine status to avoid repeated API calls
- Integrate with machine SSH for live status checks
- Add --json flag for programmatic access
- Support filtering and sorting options

---

### Story 3.4: Machine Removal Process

As an Arda user,
I want to remove machines from management while preserving historical data,
So that I can clean up my configuration without losing important information.

**Acceptance Criteria:**

**Given** I have a machine I no longer need
**When** I run `arda machines remove myserver`
**Then** the machine is removed from active management

**And** Configuration files are archived (not deleted)
**And** Machine is removed from arda.nix nixosConfigurations
**And** User confirms the removal action
**And** Archive location is documented for future reference

**Prerequisites:** Story 3.3 completed

**Technical Notes:**

- Archive to .archive/ directory with timestamp
- Keep all historical configurations for audit purposes
- Remove from active monitoring systems
- Provide restore procedure if needed

---

## Epic 4: Service/Feature/Role Architecture

Implement the core differentiator - hierarchical organization system enabling composable, reusable infrastructure components.

### Story 4.1: Service Definition System

As an Arda user,
I want to define individual Services as atomic building blocks,
So that I can create reusable, tested components for my infrastructure.

**Acceptance Criteria:**

**Given** I have an Arda project
**When** I create a service definition in services/
**Then** the service is available for composition into features

**And** Services follow established Nix module patterns
**And** Service definitions include configuration options and defaults
**And** Services are independently testable
**And** Documentation is generated for each service

**Prerequisites:** Epic 3 completed

**Technical Notes:**

- Create services/ directory structure
- Use NixOS module system for service definitions
- Include options.nix for configuration schema
- Add examples for common service patterns
- Reference: postgresql-service, nginx-service patterns

---

### Story 4.2: Feature Composition System

As an Arda user,
I want to compose Features as combinations of related Services,
So that I can group services into cohesive capability sets.

**Acceptance Criteria:**

**Given** I have multiple services defined
**When** I create a feature that combines them
**Then** the feature orchestrates the services into a unified capability

**And** Features can include 2-10 related services
**And** Service dependencies are automatically resolved
**And** Features provide simplified configuration interface
**And** Features can be reused across different roles

**Prerequisites:** Story 4.1 completed

**Technical Notes:**

- Create features/ directory structure
- Compose services using Nix module imports
- Handle service interdependencies
- Provide feature-level configuration options
- Example: caching-feature combines attic + postgres + minio

---

### Story 4.3: Role Assignment System

As an Arda user,
I want to define Roles as machine-level assignments combining multiple Features,
So that I can assign complete functionality sets to machines with a single declaration.

**Acceptance Criteria:**

**Given** I have features defined
**When** I create a role combining multiple features
**Then** the role represents a complete, deployable functionality unit

**And** Roles are assigned to machines via arda.nix
**And** Role composition is validated before deployment
**And** Role dependencies are automatically resolved
**And** Role documentation describes all included capabilities

**Prerequisites:** Story 4.2 completed

**Technical Notes:**

- Create roles/ directory structure
- Use Nix module composition for role definitions
- Validate role composition at definition time
- Add role preview command
- Example: nix-cache role includes caching-feature + networking + firewall

---

### Story 4.4: Role Composition Preview

As an Arda user,
I want to preview role composition before applying to machines,
So that I can understand what will be deployed and validate the configuration.

**Acceptance Criteria:**

**Given** I have defined roles
**When** I run `arda roles preview <rolename>`
**Then** I see a detailed breakdown of the role composition

**And** Preview shows all included features and services
**And** Configuration options and their values are displayed
**And** Dependencies and potential conflicts are highlighted
**And** Preview can be generated for any role without deployment

**Prerequisites:** Story 4.3 completed

**Technical Notes:**

- Parse role definition to build composition tree
- Display hierarchical view (Role → Features → Services)
- Show resolved configuration values
- Add option to export as JSON or diagram
- Integrate with machine assignment preview

---

### Story 4.5: Machine Role Assignment

As an Arda user,
I want to assign roles to machines via declarative arda.nix configuration,
So that I can define my infrastructure topology clearly and simply.

**Acceptance Criteria:**

**Given** I have roles defined
**When** I add role assignments to arda.nix
**Then** machines receive all configured roles upon deployment

**And** Multiple roles can be assigned to a single machine
**And** Role assignments are validated before deployment
**And** Configuration changes are tracked in version control
**And** Assignment changes take effect on next deployment

**Prerequisites:** Story 4.4 completed

**Technical Notes:**

- Use NixOS module system for role assignment
- Generate nixosConfigurations from role assignments
- Validate role compatibility at assignment time
- Support role overrides per machine
- Add documentation on arda.nix structure

---

## Epic 5: Template System

Provide built-in templates and customization system for common infrastructure patterns.

### Story 5.1: Built-in Template Library

As an Arda user,
I want to apply built-in templates to machines via `arda templates apply`,
So that I can quickly set up common configurations without manual work.

**Acceptance Criteria:**

**Given** I have a machine created
**When** I run `arda templates apply disk-single-zfs myserver`
**Then** the template is applied to the machine configuration

**And** Template generates appropriate hardware and configuration files
**And** Template variables are validated before application
**And** Available templates can be listed with descriptions
**And** Templates include documentation and examples

**Prerequisites:** Epic 4 completed

**Technical Notes:**

- Create templates/ directory with built-in templates
- Support template variables with validation
- Include disk layout templates (single-disk ZFS, multi-disk, etc.)
- Add service configuration templates
- Reference clan-core template patterns

---

### Story 5.2: Template Variable Customization

As an Arda user,
I want to customize template variables to match my specific requirements,
So that templates can be adapted for different use cases.

**Acceptance Criteria:**

**Given** I apply a template
**When** I specify custom variable values
**Then** the template is applied with my customizations

**And** Variable validation ensures values are correct format
**And** Default values are provided for optional variables
**And** Interactive mode prompts for required variables
**And** Customizations are saved in machine configuration

**Prerequisites:** Story 5.1 completed

**Technical Notes:**

- Implement template variable system with types and validation
- Support interactive and non-interactive modes
- Store template customizations in machine config
- Add --vars-file option for bulk variable setting
- Document variable schema for each template

---

### Story 5.3: Custom Template Creation

As an Arda user,
I want to create custom templates for recurring patterns,
So that I can reuse my own templates across projects.

**Acceptance Criteria:**

**Given** I have a working machine configuration
**When** I run `arda templates create my-template`
**Then** a custom template is created from the configuration

**And** Template can be parameterized with variables
**And** Custom templates are stored in templates/ directory
**And** Template can be applied to other machines
**And** Custom templates are listed alongside built-in templates

**Prerequisites:** Story 5.2 completed

**Technical Notes:**

- Extract machine configuration as template
- Generate template variable definitions
- Support custom template metadata and documentation
- Add validation for custom templates
- Enable template sharing via git

---

### Story 5.4: Template Documentation and Listing

As an Arda user,
I want to list available templates and view documentation,
So that I can understand what templates exist and how to use them.

**Acceptance Criteria:**

**Given** I want to see available templates
**When** I run `arda templates list`
**Then** I see all templates with descriptions and usage examples

**And** Built-in and custom templates are shown separately
**And** Each template shows required and optional variables
**And** Documentation includes example usage
**And** Search and filter options are available

**Prerequisites:** Story 5.3 completed

**Technical Notes:**

- Generate template metadata automatically
- Create template documentation from definitions
- Support category-based organization
- Add --detailed flag for full documentation
- Integrate with --help for individual templates

---

## Epic 6: Secret Management (Priority Focus)

Build critical security infrastructure with sops-nix integration, age key distribution, and encrypted secret storage.

### Story 6.1: Age Key Generation and Distribution

As an Arda user,
I want to generate and distribute age keys securely,
So that I can encrypt secrets for specific machines and roles.

**Acceptance Criteria:**

**Given** I need to manage secrets
**When** I run the key generation process
**Then** age keys are created and distributed to authorized machines

**And** Private keys are stored securely with 600 permissions
**And** Public keys are distributed to machines via sops-nix
**And** Key rotation process is documented and tested
**And** Keys are never logged or displayed in plaintext

**Prerequisites:** Epic 5 completed

**Technical Notes:**

- Integrate with age-keygen for key creation
- Configure .sops.yaml with machine-specific public keys
- Use sops-nix for automatic key distribution
- Implement secure key backup procedures
- Reference sops-nix documentation for best practices

---

### Story 6.2: Automatic Secret Encryption

As an Arda user,
I want all secrets to be automatically encrypted via sops-nix,
So that no plaintext secrets are ever stored in version control.

**Acceptance Criteria:**

**Given** I add secrets to my configuration
**When** I commit to version control
**Then** all secrets are encrypted automatically before storage

**And** Secret files are encrypted with appropriate public keys
**And** Encrypted files have .enc. extension
**And** Plaintext files are excluded via .gitignore
**And** Decryption works on authorized machines automatically

**Prerequisites:** Story 6.1 completed

**Technical Notes:**

- Configure sops to encrypt all secret files
- Generate .sops.yaml with proper key management
- Implement pre-commit hook for secret validation
- Use .gitignore to prevent plaintext commits
- Test encryption/decryption workflow thoroughly

---

### Story 6.3: Role-Based Secret Access

As an Arda user,
I want machine-specific secrets to be accessible only to authorized roles,
So that I can enforce security boundaries in my infrastructure.

**Acceptance Criteria:**

**Given** I have role-based infrastructure
**When** I assign roles to machines
**Then** machines receive only the secrets required for their roles

**And** Secret access is enforced at deployment time
**And** Unauthorized machines cannot decrypt secrets
**And** Secret access patterns are documented
**And** Security audit trail is maintained

**Prerequisites:** Story 6.2 completed

**Technical Notes:**

- Map role assignments to secret access policies
- Configure sops-nix with role-based encryption
- Validate secret access at configuration generation
- Add security documentation for secret management
- Test unauthorized access scenarios

---

### Story 6.4: Secret Rotation Workflow

As an Arda user,
I want to rotate secrets without manual re-encryption across all machines,
So that I can maintain security hygiene with minimal effort.

**Acceptance Criteria:**

**Given** I need to rotate secrets
**When** I run the rotation command
**Then** secrets are updated and redistributed to authorized machines

**And** Rotation process preserves secret access policies
**And** Old secrets are securely archived
**And** Rotation can be rolled back if needed
**And** Process works across multiple machines simultaneously

**Prerequisites:** Story 6.3 completed

**Technical Notes:**

- Implement sops secret rotation workflow
- Automate key distribution for rotated secrets
- Maintain rotation history for audit purposes
- Support rollback to previous secret versions
- Document rotation procedures for operators

---

### Story 6.5: Secret Operation Security

As an Arda user,
I want all secret operations to produce no plaintext output,
So that secrets remain secure throughout the entire lifecycle.

**Acceptance Criteria:**

**Given** I perform any secret operation
**When** I run arda commands
**Then** no secrets appear in CLI output or logs

**And** Commands that handle secrets have appropriate warnings
**And** Logs redact any potential secret data
**And** Debug modes don't expose secrets
**And** Security audit verifies no plaintext exposure

**Prerequisites:** Story 6.4 completed

**Technical Notes:**

- Audit all secret-handling code paths
- Implement secret redaction in logging
- Add --quiet flag for sensitive operations
- Secure temporary file handling
- Complete security review of secret workflow

---

## Epic 7: Configuration Abstraction Layer

Build the core library (arda-core.lib.arda) that abstracts Nix complexity and generates configurations automatically.

### Story 7.1: Core Library Structure

As an Arda user,
I want a clean library interface (arda-core.lib.arda) for configuration,
So that I can declare my infrastructure without understanding Nix module internals.

**Acceptance Criteria:**

**Given** I have roles and machines defined
**When** I use arda-core.lib.arda in my configuration
**Then** my simple declarations generate full NixOS configurations

**And** Library provides clear, documented interface
**And** Interface hides complexity of module composition
**And** Default configurations work out of the box
**And** Library is versioned and backward compatible

**Prerequisites:** Epic 6 completed

**Technical Notes:**

- Create lib/arda.nix with exported interface functions
- Design clean API for role and machine configuration
- Abstract Nix module complexity behind library functions
- Provide comprehensive documentation and examples
- Reference clan-lib patterns for inspiration

---

### Story 7.2: Automatic nixosConfigurations Generation

As an Arda user,
I want the library to automatically generate nixosConfigurations from directory structure,
So that I don't need to manually maintain NixOS configuration mappings.

**Acceptance Criteria:**

**Given** I have machines/ and roles/ directories
**When** I import arda-core.lib.arda
**Then** nixosConfigurations are generated automatically

**And** Each machine gets configuration based on assigned roles
**And** Configuration generation is deterministic
**And** Changes to directory structure update configurations
**And** Generation happens at nixos-rebuild time

**Prerequisites:** Story 7.1 completed

**Technical Notes:**

- Scan directory structure to build machine-role mappings
- Generate nixosConfigurations using Nix module system
- Handle role composition and dependency resolution
- Implement change detection for efficient updates
- Test generation with multiple machine configurations

---

### Story 7.3: Machine Configuration Overrides

As an Arda user,
I want to override default configurations per machine,
So that I can customize specific machines without duplicating role definitions.

**Acceptance Criteria:**

**Given** I have a machine with assigned roles
**When** I add override configuration to machines/<hostname>/
**Then** the overrides are applied to the generated configuration

**And** Override system is documented and predictable
**And** Multiple override files are merged correctly
**And** Override precedence is clearly defined
**And** Validation ensures overrides don't break configuration

**Prerequisites:** Story 7.2 completed

**Technical Notes:**

- Implement override system using Nix module priorities
- Support multiple override files with clear merging rules
- Document override patterns in user guide
- Add validation for common override mistakes
- Provide examples of valid override use cases

---

### Story 7.4: Configuration Validation System

As an Arda user,
I want configuration changes validated before deployment,
So that I can catch errors before they cause production issues.

**Acceptance Criteria:**

**Given** I make changes to my configuration
**When** I run validation
**Then** all configuration issues are identified before deployment

**And** Validation catches Nix syntax errors
**And** Configuration consistency is checked
**And** Role composition conflicts are detected
**And** Validation provides actionable error messages

**Prerequisites:** Story 7.3 completed

**Technical Notes:**

- Integrate Nix configuration validation
- Check role compatibility and dependency resolution
- Validate role assignments and feature composition
- Implement comprehensive test suite for validation
- Add CI validation for all configuration changes

---

### Story 7.5: Clan Migration Compatibility

As an Arda user,
I want to migrate existing clan configurations with minimal modifications,
So that I can transition from clan to Arda without starting from scratch.

**Acceptance Criteria:**

**Given** I have an existing clan configuration
**When** I run the migration tool
**Then** my configuration is converted to Arda format

**And** Direct service definitions are preserved
**And** Migration creates Arda-compatible structure
**And** Migration report shows what changed
**And** Configuration works identically after migration

**Prerequisites:** Story 7.4 completed

**Technical Notes:**

- Analyze clan configuration patterns
- Create migration script for common structures
- Preserve existing service definitions
- Generate documentation of migration changes
- Test migration with example clan configurations

---

## Epic 8: Update & Maintenance Framework

Implement flake-based update workflow enabling conflict-free updates and decade-scale sustainability.

### Story 8.1: Conflict-Free Update Workflow

As an Arda user,
I want to update Arda core via `nix flake update` without merge conflicts,
So that I can safely incorporate new features and security updates.

**Acceptance Criteria:**

**Given** I have a working Arda installation
**When** I run `nix flake update`
**Then** all dependencies are updated without configuration conflicts

**And** Update process preserves my customizations
**And** No manual merge resolution is required
**And** Update can be tested before applying to production
**And** Rollback to previous version is supported

**Prerequisites:** Epic 7 completed

**Technical Notes:**

- Use flake pinning to prevent automatic updates
- Create update test environment for validation
- Implement rollback procedure using flake.lock
- Document update best practices
- Add update verification checklist

---

### Story 8.2: Customization Preservation

As an Arda user,
I want my customizations to remain intact through core framework updates,
So that my configuration investment is protected over time.

**Acceptance Criteria:**

**Given** I have customized my Arda configuration
**When** I update to a new core version
**Then** all my customizations remain exactly as I defined them

**And** Custom roles, features, and services are preserved
**And** Machine-specific overrides remain unchanged
**And** Template customizations are maintained
**And** Update process validates customizations compatibility

**Prerequisites:** Story 8.1 completed

**Technical Notes:**

- Isolate user customizations from core framework
- Implement compatibility checks for custom code
- Provide migration guidance for breaking changes
- Test preservation with complex custom configurations
- Document customization best practices

---

### Story 8.3: Version Rollback Capability

As an Arda user,
I want to rollback to previous core version if update causes issues,
So that I can recover quickly from problematic updates.

**Acceptance Criteria:**

**Given** I have updated to a problematic version
**When** I run the rollback command
**Then** Arda returns to the previous working version

**And** Rollback process is documented and tested
**And** Previous configuration state is restored
**And** Rollback can be performed from any state
**And** Rollback preserves all user data and customizations

**Prerequisites:** Story 8.2 completed

**Technical Notes:**

- Track previous working flake.lock versions
- Implement automated rollback procedure
- Preserve user data during rollback
- Test rollback from various problematic states
- Document rollback procedures in troubleshooting guide

---

### Story 8.4: Update Compatibility Validation

As an Arda user,
I want update workflow to validate configuration compatibility,
So that I can catch incompatibilities before they cause deployment failures.

**Acceptance Criteria:**

**Given** I prepare to update Arda
**When** I run pre-update validation
**Then** compatibility issues are identified before applying updates

**And** Validation checks Nix configuration syntax
**And** Compatibility with new core features is verified
**And** Deprecated features are flagged with migration guidance
**And** Validation can be run in CI for automated checking

**Prerequisites:** Story 8.3 completed

**Technical Notes:**

- Implement comprehensive configuration validation
- Check for deprecated features and provide migration paths
- Add automated compatibility testing
- Integrate validation with CI/CD pipeline
- Create compatibility matrix for version tracking

---

## Epic 9: Status & Diagnostics

Provide system health monitoring, drift detection, and clear error messaging for operational excellence.

### Story 9.1: Machine Status Overview

As an Arda user,
I want to view status of all machines and pending changes,
So that I can quickly understand the current state of my infrastructure.

**Acceptance Criteria:**

**Given** I have multiple machines deployed
**When** I run `arda status`
**Then** I see a comprehensive overview of all machines

**And** Each machine shows hostname, configuration hash, and last deployed time
**And** Status indicators show healthy, update pending, or error states
**And** Pending changes are summarized with counts
**And** Output is color-coded and easy to scan

**Prerequisites:** Epic 8 completed

**Technical Notes:**

- Query each machine for current configuration state
- Cache status information for fast display
- Implement SSH-based status checking
- Add filtering and sorting options
- Support JSON output for automation

---

### Story 9.2: Configuration Drift Detection

As an Arda user,
I want configuration drift detected and reported,
So that I can identify when machines diverge from declared state.

**Acceptance Criteria:**

**Given** I have deployed machines
**When** drift detection runs
**Then** any configuration differences are identified and reported

**And** Drift detection compares declared vs actual configuration
**And** Drift report shows specific differences
**And** Drift can be detected via SSH without agents
**And** Drift detection runs automatically on status check

**Prerequisites:** Story 9.1 completed

**Technical Notes:**

- Implement configuration comparison via Nix eval
- Use SSH to query actual machine state
- Generate detailed drift reports
- Support multiple drift detection strategies
- Add drift history tracking

---

### Story 9.3: Automatic Rollback on Failure

As an Arda user,
I want failed deployments to automatically rollback to last known good state,
So that infrastructure remains functional even when deployments fail.

**Acceptance Criteria:**

**Given** I deploy to a machine
**When** the deployment fails
**Then** the machine is automatically restored to previous working configuration

**And** Rollback completes within 5 minutes of failure detection
**And** Previous configuration is fully restored
**And** Failure details are logged for analysis
**And** Rollback can be initiated manually if needed

**Prerequisites:** Story 9.2 completed

**Technical Notes:**

- Implement deployment transaction system
- Store previous working configuration
- Automate rollback on deployment failure
- Log all rollback events with timestamps
- Add rollback verification after completion

---

### Story 9.4: Clear Error Messages and Recovery

As an Arda user,
I want clear error messages with specific recovery paths,
So that I can quickly diagnose and fix configuration issues.

**Acceptance Criteria:**

**Given** an error occurs
**When** I see the error message
**Then** I understand what went wrong and how to fix it

**And** Error messages include specific problem description
**And** Recovery steps are provided for common errors
**And** Error messages avoid Nix jargon when possible
**And** Links to relevant documentation are included

**Prerequisites:** Story 9.3 completed

**Technical Notes:**

- Implement comprehensive error handling
- Map Nix errors to user-friendly messages
- Provide context-specific recovery guidance
- Create error message style guide
- Test error scenarios and recovery procedures

---

## Epic 10: Deployment & Operations

Implement multi-machine deployment capabilities with idempotent operations and comprehensive logging.

### Story 10.1: Parallel Multi-Machine Deployment

As an Arda user,
I want to deploy multiple machines in parallel with progress tracking,
So that I can efficiently update large infrastructure deployments.

**Acceptance Criteria:**

**Given** I have multiple machines to deploy
**When** I run the deployment command
**Then** machines are deployed in parallel with real-time progress updates

**And** Deployment progress is shown per machine
**And** Failed deployments don't block other machines
**And** Parallelism is configurable (e.g., max 3 concurrent)
**And** Overall status is visible throughout deployment

**Prerequisites:** Epic 9 completed

**Technical Notes:**

- Implement parallel deployment engine
- Track deployment progress per machine
- Handle deployment failures gracefully
- Add concurrency controls and limits
- Test parallel deployment with various machine counts

---

### Story 10.2: Idempotent Operations

As an Arda user,
I want deployment operations to be idempotent,
So that running the same deployment multiple times produces consistent results.

**Acceptance Criteria:**

**Given** I have a deployed machine
**When** I run the deployment command again
**Then** the machine ends up in the same state (no changes)

**And** Re-deployment is fast when no changes exist
**And** Idempotency is verified in testing
**And** Configuration drift is detected and corrected
**And** Idempotency works across different machine states

**Prerequisites:** Story 10.1 completed

**Technical Notes:**

- Implement configuration hashing for change detection
- Skip deployment if configuration hash matches
- Use Nix's built-in idempotency guarantees
- Add idempotency tests to test suite
- Document idempotency guarantees

---

### Story 10.3: Deployment Preview

As an Arda user,
I want to preview changes before applying them to production machines,
So that I can validate deployments before making infrastructure changes.

**Acceptance Criteria:**

**Given** I have pending configuration changes
**When** I run the preview command
**Then** I see exactly what will change before deployment

**And** Preview shows configuration differences clearly
**And** Preview can be generated for any machine
**And** Preview works without SSH access to target machine
**And** Preview can be saved for audit purposes

**Prerequisites:** Story 10.2 completed

**Technical Notes:**

- Generate configuration diff using Nix
- Compare current vs proposed configuration
- Display changes in readable format
- Support multiple output formats (text, JSON, diff)
- Add preview validation for configuration changes

---

### Story 10.4: Comprehensive Deployment Logging

As an Arda user,
I want all deployment operations logged for troubleshooting and audit,
So that I can track what happened and why during deployments.

**Acceptance Criteria:**

**Given** I deploy to machines
**When** the deployment completes
**Then** comprehensive logs are created and stored

**And** Logs include timestamps and user identification
**And** Deployment actions are recorded with results
**And** Logs are stored in structured format
**And** Logs can be searched and filtered

**Prerequisites:** Story 10.3 completed

**Technical Notes:**

- Implement structured logging system
- Log all deployment actions and outcomes
- Store logs with machine identification
- Add log rotation and retention policies
- Create log analysis and reporting tools

---

<!-- End epic breakdown -->

---

## FR Coverage Matrix

**Complete Functional Requirements to Epic/Story Mapping:**

**FR1** → Epic 6, Story 6.1: Age Key Generation and Distribution
**FR2** → Epic 2, Story 2.2: Single Command Installation Workflow
**FR3** → Epic 2, Story 2.3: GitHub Repository Template Creation
**FR4** → Epic 3, Story 3.1: Machine Configuration Creation
**FR5** → Epic 3, Story 3.2: Machine Deployment Workflow
**FR6** → Epic 3, Story 3.3: Machine Status Monitoring
**FR7** → Epic 3, Story 3.4: Machine Removal Process
**FR8** → Epic 4, Story 4.1: Service Definition System
**FR9** → Epic 4, Story 4.2: Feature Composition System
**FR10** → Epic 4, Story 4.3: Role Assignment System
**FR11** → Epic 4, Story 4.5: Machine Role Assignment
**FR12** → Epic 4, Story 4.5: Machine Role Assignment
**FR13** → Epic 4, Story 4.4: Role Composition Preview
**FR14** → Epic 5, Story 5.1: Built-in Template Library
**FR15** → Epic 5, Story 5.2: Template Variable Customization
**FR16** → Epic 5, Story 5.3: Custom Template Creation
**FR17** → Epic 5, Story 5.4: Template Documentation and Listing
**FR18** → Epic 6, Story 6.2: Automatic Secret Encryption
**FR19** → Epic 6, Story 6.1: Age Key Generation and Distribution
**FR20** → Epic 6, Story 6.4: Secret Rotation Workflow
**FR21** → Epic 6, Story 6.3: Role-Based Secret Access
**FR22** → Epic 6, Story 6.5: Secret Operation Security
**FR23** → Epic 7, Story 7.1: Core Library Structure
**FR24** → Epic 7, Story 7.2: Automatic nixosConfigurations Generation
**FR25** → Epic 7, Story 7.3: Machine Configuration Overrides
**FR26** → Epic 7, Story 7.4: Configuration Validation System
**FR27** → Epic 7, Story 7.5: Clan Migration Compatibility
**FR28** → Epic 7, Story 7.5: Clan Migration Compatibility
**FR29** → Epic 7, Story 7.5: Clan Migration Compatibility
**FR30** → Epic 7, Story 7.1: Core Library Structure
**FR31** → Epic 8, Story 8.1: Conflict-Free Update Workflow
**FR32** → Epic 8, Story 8.2: Customization Preservation
**FR33** → Epic 8, Story 8.3: Version Rollback Capability
**FR34** → Epic 8, Story 8.4: Update Compatibility Validation
**FR35** → Epic 1, Story 1.2: Development Shell Configuration
**FR36** → Epic 1, Story 1.5: Testing Framework Setup
**FR37** → Epic 1, Story 1.3: Branch Management Workflow Setup
**FR38** → Epic 1, Story 1.4: Flake Configuration and Lock Management
**FR39** → Epic 9, Story 9.1: Machine Status Overview
**FR40** → Epic 9, Story 9.2: Configuration Drift Detection
**FR41** → Epic 9, Story 9.3: Automatic Rollback on Failure
**FR42** → Epic 9, Story 9.4: Clear Error Messages and Recovery
**FR43** → Epic 3, Story 3.1: Machine Configuration Creation
**FR44** → Epic 4, Story 4.1: Service Definition System
**FR45** → Epic 6, Story 6.1: Age Key Generation and Distribution
**FR46** → Epic 5, Story 5.4: Template Documentation and Listing
**FR47** → Epic 10, Story 10.1: Parallel Multi-Machine Deployment
**FR48** → Epic 10, Story 10.2: Idempotent Operations
**FR49** → Epic 10, Story 10.3: Deployment Preview
**FR50** → Epic 10, Story 10.4: Comprehensive Deployment Logging

**Coverage Summary:**

- Total FRs: 50
- Mapped to epics: 50 (100%)
- Total stories across all epics: 41
- Average stories per epic: 4.1
- Epic with most stories: Epic 6 (Secret Management) - 5 stories
- Epic with fewest stories: Epic 2 (Installation & Bootstrap) - 3 stories

---

## Summary

**✅ Epic Breakdown Complete (Initial Version)**

The epic and story breakdown for clan-core / Arda has been successfully completed, transforming 50 functional requirements into 41 implementable stories across 10 cohesive epics.

### Key Achievements

**1. Complete FR Coverage**

- All 50 functional requirements from the PRD have been mapped to epics and stories
- Every FR has a clear implementation path with detailed acceptance criteria
- No requirements are orphaned or unaddressed

**2. Foundation-First Approach**

- Epic 1 establishes solid development infrastructure before building features
- Each epic builds on previous epics, creating a logical progression
- Epic 1 Story 1.1 is project setup/infrastructure initialization as required

**3. Strategic Prioritization**

- Epic 6 (Secret Management) receives priority focus with 5 stories
- Critical security features (FR1, FR18-22, FR45) are comprehensively addressed
- The unique Service/Feature/Role architecture is properly decomposed

**4. Bite-Sized Stories**

- All 41 stories are sized for single-session completion by a development agent
- Each story includes BDD-style acceptance criteria (Given/When/Then)
- Prerequisites are clearly defined to prevent forward dependencies
- Technical notes provide implementation guidance

**5. Architectural Integrity**

- Service/Feature/Role hierarchy is fully realized across Epic 4 (5 stories)
- Flake-based update model is properly supported in Epic 8 (4 stories)
- Abstractions are designed to reduce clan-core footprint by 50%
- Migration path from clan is preserved (Epic 7, Story 7.5)

### Story Quality Validation

✅ **All functional requirements covered** - 100% FR coverage achieved
✅ **Epic 1 establishes foundation** - Proper infrastructure setup
✅ **Vertically sliced stories** - Each delivers complete functionality
✅ **No forward dependencies** - Only backward references in prerequisites
✅ **Appropriate sizing** - Single-session completion capability
✅ **Clear BDD acceptance criteria** - Testable and autonomous
✅ **Details added beyond PRD** - UI specifics, performance targets, edge cases
✅ **Domain requirements integrated** - Security, compliance properly distributed
✅ **Sequential value delivery** - Incremental capabilities enabled

### BMad Method Next Steps

This epic breakdown is the **INITIAL VERSION**. It will evolve through the workflow chain:

**1. UX Design Workflow** (if UI exists)

- Design interactions for user-facing capabilities
- UPDATE story acceptance criteria with UX specifications
- Add mockup references, flow details, interaction patterns
- Add responsive design decisions and accessibility requirements

**2. Architecture Workflow**

- Define technical implementation approach
- UPDATE story technical notes with architecture decisions
- Add data models, API contracts, tech stack choices
- Add deployment patterns and integration decisions

**3. Phase 4 Implementation**

- Stories pull context from: PRD (why) + epics.md (what/how) + UX (interactions) + Architecture (technical)
- Stories may be further refined as implementation uncovers edge cases
- This document remains the single source of truth for story details

### Implementation Readiness

The stories are now ready for:

- Assignment to development agents via `create-story` workflow
- Estimation and sprint planning
- Parallel development where dependencies allow
- Validation through proof-of-concept implementations

### Critical Success Factors

1. **Secret Management Priority** - Epic 6 must be resourced appropriately given its criticality
2. **Foundation Quality** - Epic 1 must be rock-solid to support all subsequent work
3. **Incremental Validation** - Each story should be tested before moving to next
4. **Documentation First** - Stories include technical notes for maintainability
5. **Decade-Scale Thinking** - All design decisions evaluated for long-term viability

---

**Created:** epics.md with comprehensive epic and story breakdown

**Total:** 10 epics, 41 stories, 50 functional requirements fully covered

**Next Steps:** UX Design workflow (add interaction details) → Architecture workflow (add technical decisions) → Phase 4 Implementation

**Important:** This is a living document that will be updated as you progress through the workflow chain. The epics.md file will evolve with UX and Architecture inputs before implementation begins.

---

_For implementation: Use the `create-story` workflow to generate individual story implementation plans from this epic breakdown._

_This document will be updated after UX Design and Architecture workflows to incorporate interaction details and technical decisions._
