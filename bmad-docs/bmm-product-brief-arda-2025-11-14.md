# Product Brief: Arda

**Date:** 2025-11-14
**Author:** Lord
**Context:** Infrastructure Management Tool (Greenfield with Brownfield Foundation)

---

## Executive Summary

Arda is a minimal, sustainable infrastructure management tool for NixOS, designed as a community-friendly fork of the "clan" project. The tool aims to provide a clean separation between core framework and user configurations, enabling decades-long infrastructure evolution without update conflicts. Primary use is self-management, with public distribution as a key design driver. The approach prioritizes flake-based updates, sops-nix secret management, and a CLI-driven workflow that abstracts configuration complexity.

---

## Core Vision

### Problem Statement

The current landscape of NixOS configuration management presents a fundamental update problem. Traditional monolithic flakes create merge conflicts when users customize configurations and the developer releases updates. This forces users to either avoid updates (security and feature risks) or lose customizations (maintenance burden). Additionally, the all-in-one repository model doesn't scale well for long-term infrastructure management where the configuration must evolve over decades.

Most existing solutions require users to either:

1. Fork and maintain their own configuration fork indefinitely
2. Edit configuration files directly, creating update conflicts
3. Use complex git rebase workflows to incorporate upstream changes

These approaches don't align with sustainable, long-term infrastructure management where configurations must evolve while preserving user customizations.

### Proposed Solution

Arda provides a clean separation of concerns through:

**Abstraction Layer**: Like clan, Arda uses a library approach where the core configuration logic lives in arda-core, while user configurations remain minimal and safe to edit. Users run `nix flake update` rather than `git pull`, eliminating merge conflicts.

**CLI-First Workflow**: A command-line tool (arda-cli) that handles machine creation, configuration generation, and deployment, abstracting complex NixOS configuration behind simple commands.

**Flake-Based Distribution**: Users pin to a specific arda-core version via flake inputs, making updates predictable and reversible. No git operations required.

**Integrated Secret Management**: Native sops-nix integration for age-based encryption, with secrets automatically managed and distributed to machines.

**Minimal User Configuration**: User repositories contain only essential configuration files (clan.nix equivalent), with machine-specific configs auto-generated based on directory structure.

### Key Differentiators

- **Service/Feature/Role Architecture**: Unlike clan's service-only approach, Arda organizes functionality into Services → Features → Roles hierarchy. Roles are assigned to machines, providing composable functionality.
  - *Example*: A "nix-cache" role combines attic-server, postgresql-server, and minio-server services into a coherent feature
- **Opinionated Defaults**: Deliberately opinionated toward specific technologies (ZFS root, impermanence, specific service stacks)
- **Minimal Footprint**: Aggressive removal of unnecessary features from clan-core, keeping only essential scaffolding
- **Template-Driven Configuration**: Built-in templating system for common patterns (disk layouts, service configurations)
- **Decade-Scale Design**: Every design decision considers multi-decade maintenance and evolution
- **Self-Use First**: Optimized for single-operator management while remaining public-ready
- **Educational Focus**: Designed to help Lord learn Nix while building something production-worthy

---

## Target Users

### Primary Users

**Lord (Primary)**: Veteran Linux user transitioning to NixOS for full infrastructure replacement. Learning Nix while building a tool for decades-long use. Values simplicity, security, and maintainability over cutting-edge features.

**Technical Self-Hosters**: Individuals who manage multiple machines and value reproducible, declarative infrastructure. Want the power of NixOS without the complexity of managing monolithic configurations.

### Secondary Users

**NixOS Community Members**: Those seeking an alternative to existing configuration management tools, particularly attracted to the clan approach but wanting more opinionated defaults or simpler core.

**Long-Term Infrastructure Teams**: Small teams (1-5 people) managing production infrastructure who need sustainable configuration evolution without merge conflicts.

---

## Success Metrics

### User Metrics

- Successful installation and machine deployment without manual intervention
- Ability to update arda-core via `nix flake update` without configuration conflicts
- Zero secrets committed to version control
- Machine deployment success rate >95% on first attempt

### Technical Metrics

- Lines of code reduced from clan-core baseline (target: 50% reduction in arda-v1)
- Number of external dependencies minimized
- Documentation completeness (every feature documented with examples)
- Test coverage for critical paths (machine creation, deployment, secret management)

### Learning Metrics

- Lord's Nix proficiency progression (measurable via feature complexity)
- Time to deploy first machine (target: <1 hour from clone to running machine)
- Configuration change success rate (updates apply without manual intervention)

---

## MVP Scope

### Core Features (Essential for Launch)

1. **Installation Workflow**
   - `nix run` installation similar to clan
   - Age key generation
   - Arda name prompt and directory creation
   - Basic flake.nix and arda.nix generation
   - GitHub repository creation guidance

2. **Machine Management**
   - `arda machine create <hostname>` - Create machine configuration
   - `arda machines install <hostname>` - Deploy to target host
   - Directory structure auto-generation (machines/<hostname>/)

3. **Service/Feature/Role Architecture** (Core Differentiator)
   - `arda roles` - Manage role definitions (composable functionality units)
   - `arda features` - Manage feature definitions (groupings of services)
   - `arda services` - Manage individual service definitions
   - Role assignment to machines via arda.nix configuration
   - Directory structure: `roles/`, `features/`, `services/`

4. **Template System**
   - `arda templates apply <template-name> <machine>` - Apply disk layout templates
   - Built-in templates: `disk single-disk-zfs` (minimal ZFS root layout)
   - Template system extensible for future impermanent ZFS layouts
   - Template variables and customization support

5. **Secret Management Integration** (Priority Focus)
   - Automatic sops-nix configuration
   - Age key distribution to machines
   - Secrets directory structure generation
   - Secret rotation capability
   - Seamless integration with role/service model

6. **Abstraction Layer**
   - arda-core.lib.arda library function
   - Automatic nixosConfigurations generation from machines directory
   - Module system for roles, features, and services
   - Compatibility layer for clan-style direct service definitions

7. **Development Environment**
   - `nix develop` shell with arda-cli available
   - Branch management helpers (clan-core reference, arda-v1 development)
   - Basic flake.lock management

### Out of Scope for MVP

- Advanced service templates (beyond basic system services)
- Multi-user/multi-tenant features
- Web UI or dashboard
- Advanced networking features (beyond what clan provides minimally)
- Integration with external tools beyond Nix ecosystem
- Backup/restore functionality
- Monitoring and metrics collection
- High availability or clustering features

### MVP Success Criteria

1. Can successfully create a minimal Arda installation
2. Can deploy a single NixOS machine from Arda configuration
3. Secrets are properly encrypted and accessible on deployed machines
4. Can update to newer arda-core version via `nix flake update`
5. User configuration remains editable without conflicts after updates
6. Basic machine configuration can be customized via arda.nix

### Future Vision (Post-MVP)

**Immediate Post-MVP Priorities**:

- Expand template library (impermanence ZFS layouts, complex disk configurations)
- Core service templates (SSH, firewall, basic networking)
- Role library (nix-cache, web-server, database-server, etc.)

**Medium Term**:

- Opinionated module system (pre-configured templates for common services)
- Documentation portal with examples
- Migration tools from other NixOS configuration methods

**Long Term**:

- Community template library
- Integration with additional Nix ecosystem tools
- Automated testing for configurations
- Package distribution system for sharing roles/features

---

## Financial Considerations

**Development Investment**:

- Time: Significant learning investment in Nix and Python
- Infrastructure: VM hosting for Forgejo instance
- Opportunity Cost: Delayed infrastructure migration during development

**Operational Costs**:

- Git hosting (Forgejo VM - minimal)
- Domain/hosting if made public (optional)
- Maintenance time over decades (scales with feature set)

**Cost Avoidance**:

- Avoiding vendor lock-in to commercial infrastructure tools
- No licensing fees for configuration management
- Reduced maintenance overhead through declarative approach

---

## Technical Preferences

### Platform Focus

- Primary: x86_64-linux (current focus)
- Future: aarch64-linux, darwin (as needed)

### Technology Stack (Inherited from Clan)

- NixOS for configuration management
- Nix flakes for packaging and distribution
- Nix language for configuration
- Python for CLI tool
- sops-nix for secret management
- age for encryption

### Integration Requirements

- Forgejo for version control hosting
- Minimal external dependencies
- Compatibility with standard NixOS workflows

---

## Risks and Assumptions

### Key Risks

1. **Skill Gap Risk**: Learning Nix and Python while building critical infrastructure
   - *Mitigation*: Start with minimal MVP, incremental learning, extensive testing

2. **Maintenance Burden**: Decade-scale maintenance commitment
   - *Mitigation*: Minimize features, focus on simplicity, thorough documentation

3. **Community Adoption Risk**: Limited public interest vs. clan
   - *Mitigation*: Self-use primary, public distribution secondary

4. **Technical Debt**: Rushing to migrate infrastructure before tool maturity
   - *Mitigation*: Clear MVP criteria, don't start production migration until proven

### Critical Assumptions

- Clan-core architecture is sound and can be safely reduced
- NixOS will remain viable for decades
- Lord can learn sufficient Python/Nix for maintenance
- sops-nix will continue to be maintained
- Single-operator management model is sufficient

### Open Questions

1. **What is the minimal subset of clan-core to achieve the MVP?** (Priority 1 - must answer before development)
2. How to structure the service/feature/role hierarchy in Nix modules for maximum composability?
3. **Where to draw the line on opinionated defaults vs. configurability?** (ZFS/impermanence baked in vs. optional)
4. What level of testing is required before production use? (Acceptable risk vs. time investment)
5. How to handle breaking changes in arda-core while maintaining user update path?
6. Should migration from monolithic NixOS configs be supported in MVP or later?

---

## Timeline Constraints

**URGENT: Days to Weeks Timeline** - This is not a months-long project

**Current Phase**: Planning and design (IN PROGRESS - TODAY)
**Immediate Next Phase**: Arda-v1 creation (START IMMEDIATELY after brief)
**Development Phase**: Iterative extraction and testing (INTENSIVE - Days/Weeks)
**Testing Phase**: Minimal deployment validation (Parallel with development)
**Migration Phase**: Infrastructure transition (AFTER MVP proven)

**Critical Milestones** (Days/Weeks, not months):

1. **TODAY**: Complete product brief and architecture design
2. **TODAY/TOMORROW**: Create GitHub repo and initialize arda-v1 branch
3. **THIS WEEK**: Map minimal clan-core subset needed for MVP
4. **WEEK 1-2**: First working arda-cli with basic installation workflow
5. **WEEK 2-3**: Secrets management working (sops-nix integration)
6. **WEEK 3-4**: Service/feature/role system functional
7. **WEEK 4+**: MVP complete - deploy first test machine

**Accelerators Needed**:

- Intensive focus on secret management (highest risk/complexity)
- Parallel development and testing
- Minimize scope creep - focus ONLY on MVP features

---

## Organizational Context

**Strategic Alignment**:

- Long-term infrastructure modernization initiative
- Shift from traditional Linux administration to declarative configuration
- Knowledge transfer and skill development in modern configuration management

**Stakeholder Considerations**:

- Single stakeholder (Lord) simplifies decision-making
- No organizational change management required
- No compliance requirements (self-use)
- Documentation investment critical for future maintenance

---

## Workflow Strategy

The development approach follows a brownfield methodology with greenfield execution:

**Repository Setup**:

- Create GitHub repo: `https://github.com/lorddevi/arda-core`
- Preserve current `clan-core` main branch as `clan-core` reference branch
- This maintains easy access to original implementation for comparison

**Extraction Workflow** (Iterative, days/weeks timeline):

1. **Examine Phase**: Study specific feature in `clan-core` branch
2. **Implement Phase**: Create minimal version in `arda-v1` branch
3. **Test Phase**: Validate each addition before proceeding
4. **Iterate**: Repeat for next feature until MVP complete
5. **Consolidate**: Merge `arda-v1` → `main` → `master`

**Development Commands**:

- Daily workflow: Compare `clan-core` → `arda-v1`, implement minimal version, test
- Multiple branches for experimentation: `arda-v1`, `arda-v2`, etc. until MVP achieved
- Continuous reference to `clan-core` branch throughout development

**Key Principles**:

- One small, testable story at a time
- Validate each component in isolation before adding next
- Document decisions and lessons learned
- Focus on secrets management integration (highest priority)
- Build service/feature/role architecture from day one

**Timeline**: Intensive development cycle targeting MVP completion in **days to weeks**, not months.

---

*This Product Brief captures the vision for Arda, a minimal, sustainable NixOS infrastructure management tool.*

*It reflects a self-use project designed for public distribution, with decades-long maintainability as a core design principle.*
