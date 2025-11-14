# clan-core - Product Requirements Document

**Author:** Lord
**Date:** 2025-11-14
**Version:** 1.0

---

## Executive Summary

Arda addresses a critical problem in the NixOS ecosystem: the fundamental conflict between configuration customization and upstream updates. Traditional monolithic flakes force users into an unsustainable choice—either avoid updates (risking security and features) or lose customizations during updates (creating maintenance burdens).

Arda provides a clean abstraction layer that separates core framework (arda-core) from user configurations, enabling predictable updates via `nix flake update` without merge conflicts. Unlike existing solutions that require forking or complex git workflows, Arda leverages flake pinning for predictable, reversible updates while preserving user customizations indefinitely.

The vision is simple yet powerful: infrastructure configurations that evolve gracefully over decades, with the same clean separation that has made Linux distributions sustainable. Arda makes NixOS configuration management accessible to self-hosters and small teams who want the power of declarative infrastructure without the complexity of managing monolithic configurations.

### What Makes This Special

**Service/Feature/Role Hierarchical Architecture**

Unlike clan's flat service-only model, Arda implements a three-tier hierarchy:

1. **Services** - Individual, composable components (e.g., attic-server, postgresql-server)
2. **Features** - Groupings of related services that deliver specific capabilities
3. **Roles** - Composable functionality units assigned to machines

This hierarchy enables true composability. Example: A "nix-cache" role seamlessly combines attic-server, postgresql-server, and minio-server into a coherent feature set that can be assigned to any machine.

**Opinionated Defaults with Flexibility**
Deliberately opinionated toward specific technologies (ZFS root, impermanence, sops-nix) while maintaining user configurability. Like Arch Linux—but for infrastructure management.

**Decade-Scale Design Philosophy**
Every decision considers 10-20 year maintenance implications. Design patterns that remain stable over time, avoiding trendy but transient approaches.

**Flake-Native Update Model**
Users update via `nix flake update` rather than git operations, eliminating merge conflicts entirely. Pinning makes updates predictable and reversible.

**Educational Investment**
Designed from the ground up to help Lord learn Nix while building production-worthy infrastructure. Every component is documented with learning context, creating a sustainable knowledge base.

---

## Project Classification

**Technical Type:** CLI Developer Tool / Infrastructure Management System
**Domain:** Infrastructure/DevOps Automation
**Complexity:** Medium-High Complexity

**Technical Classification:** CLI-based Infrastructure Management Tool

**Architectural Approach:**

- Flake-based distribution model (like clan)
- Service/Feature/Role hierarchical organization (unique differentiator)
- Template-driven configuration generation
- CLI-first workflow for all operations
- Self-use optimized with public distribution readiness

**Development Strategy:**

- Brownfield foundation (derived from clan-core)
- Greenfield execution (new architecture from ground up)
- Iterative extraction and testing methodology
- Days/weeks aggressive timeline with MVP focus

**Target Complexity:** Medium-High

- Technical: NixOS, Python, sops-nix integration required
- Operational: Decade-scale maintenance considerations
- Learning: Developer tool requiring Nix proficiency
- Scope: Focused but with deep integration requirements

**Production Readiness Considerations:**

- Educational focus (primary user learning while building)
- Self-use first approach (real-world validation guaranteed)
- Public-ready architecture (community distribution enabled)
- Extensive documentation emphasis (future maintainability)

---

## Success Criteria

**Installation & Setup Success:**

- User can complete initial Arda installation in under 1 hour from clone to running configuration
- No manual NixOS configuration knowledge required beyond basic terminal familiarity
- All prerequisites (age keys, flake setup, initial configuration) completed via `nix run` command

**Update & Maintenance Success:**

- Users can update Arda via `nix flake update` without any merge conflicts
- User customizations remain intact through core framework updates (verified across multiple update cycles)
- Configuration changes apply successfully without manual intervention (target: >95% first-try success rate)

**Secret Management Success:**

- Zero secrets committed to version control (100% compliance)
- All secrets automatically encrypted via sops-nix and distributed securely to deployed machines
- Secret rotation works seamlessly across all machines with role-based access

**Deployment Success:**

- First machine deployment completes successfully without manual configuration
- Multi-machine orchestration works reliably across 2-5 machines
- Machine configuration matches declared state in arda.nix (no drift)

**Learning & Documentation Success:**

- Documentation enables self-service problem resolution (no ongoing mentorship required)
- Each feature has working examples in the documentation
- Lord's Nix proficiency progression measurable via complexity of implemented features

**Architectural Success:**

- Service/Feature/Role hierarchy proves composable and extensible (not just theoretical)
- Flake pinning enables rollback to any previous Arda version
- Code footprint reduced by 50% from clan-core baseline while maintaining full functionality

### Business Metrics

**Technical Debt Metrics:**

- Lines of code in arda-core compared to clan-core (target: 50% reduction)
- Number of external dependencies (target: minimal, less than clan-core)
- Test coverage for critical paths (machine creation, deployment, secret management)
- Documentation completeness percentage (target: 100% for all MVP features)

**User Success Metrics:**

- Time to first successful deployment (target: <1 hour)
- Update success rate without conflicts (target: >95%)
- Configuration change success rate on first attempt (target: >95%)
- Number of roles/features/services successfully composed

**Maintenance Metrics:**

- Time required to add new service template to library
- Time required to implement new role from existing features
- Time to diagnose and resolve configuration issues using documentation

**Community Metrics (Secondary):**

- External contributors able to use Arda without direct support
- Documentation enables community-contributed templates
- Public GitHub repository demonstrates sustainable maintenance approach

---

## Product Scope

### MVP - Minimum Viable Product

**Core Infrastructure Management:**

1. **Installation Workflow**
   - `nix run` installation similar to clan
   - Age key generation for encryption
   - Arda name prompt and directory creation
   - Basic flake.nix and arda.nix generation
   - GitHub repository creation guidance

2. **Machine Management**
   - `arda machine create <hostname>` - Create machine configuration
   - `arda machines install <hostname>` - Deploy to target host
   - Directory structure auto-generation (machines/<hostname>/)
   - Basic configuration generation from declarative definitions

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

**MVP Success Definition:**

- Successfully create minimal Arda installation
- Deploy single NixOS machine from Arda configuration
- Secrets properly encrypted and accessible on deployed machines
- Update to newer arda-core version via `nix flake update` without conflicts
- User configuration remains editable without conflicts after updates

### Growth Features (Post-MVP)

**Immediate Post-MVP (Weeks 1-8 after MVP):**

- **Expanded Template Library**
  - Impermanence ZFS layouts
  - Complex disk configurations (LVM, multiple drives)
  - Boot loader configurations (GRUB, systemd-boot)

- **Core Service Templates**
  - SSH server configuration
  - Firewall rules (basic and advanced)
  - Basic networking (DHCP, static IP)
  - Time synchronization (NTP/chrony)

- **Role Library**
  - `nix-cache` - Complete caching server (attic + postgresql + minio)
  - `web-server` - Basic web hosting capability
  - `database-server` - PostgreSQL/MySQL template
  - `mail-server` - Basic mail handling

- **Enhanced Secret Management**
  - Secret rotation automation
  - Machine-specific secret scoping
  - Integration with role-based access patterns

**Medium Term (Months 2-6):**

- **Opinionated Module System**
  - Pre-configured templates for common services
  - opinionated defaults with override capability
  - Integration with popular NixOS services

- **Documentation Portal**
  - Comprehensive documentation with examples
  - Interactive tutorials for common workflows
  - Troubleshooting guides with solutions

- **Migration Tools**
  - Import existing NixOS configurations
  - Import from other configuration management tools (Ansible, Puppet, etc.)
  - Automated migration assessment

- **Enhanced CLI**
  - `arda status` - System health overview
  - `arda update` - Integrated update workflow
  - `arda diff` - Preview configuration changes

### Vision (Future)

**Long Term Vision (6+ Months):**

- **Community Ecosystem**
  - Community template library with contribution workflow
  - Template marketplace for sharing roles/features
  - Public registry of tested configurations
  - Community-driven documentation improvements

- **Advanced Nix Integration**
  - Integration with additional Nix ecosystem tools (home-manager, nix-darwin)
  - Advanced flake workflows (multiple outputs, overlays)
  - Integration with NixOS channels and release management

- **Testing & Quality Assurance**
  - Automated testing for configuration validation
  - CI/CD integration for configuration testing
  - Integration testing for multi-machine deployments
  - Configuration drift detection and reporting

- **Package Distribution System**
  - Share roles and features via Git repositories
  - Version management for shared configurations
  - Dependency resolution for role/feature combinations
  - Public/private distribution channels

- **Advanced Infrastructure Features**
  - High availability configurations
  - Clustering and failover support
  - Backup/restore integration
  - Monitoring and metrics collection hooks

- **Enterprise Features**
  - Multi-tenant support (future consideration)
  - Audit logging for configuration changes
  - Compliance templates (SOC2, PCI-DSS, etc.)
  - Integration with enterprise secret management systems

---

---

## Innovation & Novel Patterns

**Service/Feature/Role Hierarchical Architecture**

The most significant innovation in Arda is the three-tier hierarchical organization system that goes beyond clan's flat service model. This creates a new pattern for infrastructure composition:

- **Problem Solved:** How to compose infrastructure from reusable, tested components while maintaining flexibility
- **Innovation:** Separation of concerns at three distinct levels:
  - *Services* are atomic, tested building blocks
  - *Features* are composed service combinations that deliver specific capabilities
  - *Roles* are machine-level assignments that bundle features into deployable units
- **Impact:** Enables true reusability without the complexity of microservices orchestration

**Decade-Scale Sustainable Design**

Unlike typical software projects with 2-5 year lifecycles, Arda explicitly designs for 10-20 year maintenance horizons:

- **Innovation:** Every architectural decision evaluated through decade-scale lens
- **Pattern:** Flake pinning, minimal dependencies, aggressive simplification
- **Impact:** Infrastructure that evolves with technology while preserving user customizations

**Flake-Native Update Workflow**

Rather than adopting git-based update models from traditional configuration management, Arda leverages Nix flakes for truly conflict-free updates:

- **Innovation:** `nix flake update` replaces git pull/merge operations
- **Benefit:** Updates become predictable and reversible, not destructive
- **Pattern:** All configuration managed through flake inputs, not direct git manipulation

**Educational-First Development**

An unusual approach where the development process itself becomes a learning vehicle:

- **Innovation:** Building production infrastructure specifically to learn the technology
- **Pattern:** Every feature documented with "why it works" not just "how to use it"
- **Impact:** Creates sustainable knowledge base for long-term maintenance

**Abstraction Layer with Minimal Footprint**

Instead of the typical approach of building comprehensive frameworks, Arda aggressively removes features to create minimal viable abstraction:

- **Innovation:** Code reduction as primary success metric (50% from clan-core)
- **Pattern:** Remove first, add only if essential
- **Benefit:** Lower maintenance burden over decades

### Validation Approach

**Learning-First Validation:**

- **Incremental Implementation:** Each feature built and tested before adding next
- **Real-World Testing:** Primary user (Lord) validates every component in actual use
- **Documentation-Driven:** If a feature can't be explained clearly, it's not complete
- **Self-Use Validation:** No theoretical features—all must be production-ready

**Technical Validation:**

- **Test-First for Critical Paths:**
  - Machine creation workflow (end-to-end test)
  - Secret management integration (encryption/decryption verification)
  - Update workflow (flake update without conflicts)
  - Role/feature composition (multi-service deployment test)

- **Conflict Simulation Testing:**
  - Modify user configurations
  - Update arda-core
  - Verify no merge conflicts occur
  - Test rollback to previous version

**Validation Timeline:**

- **MVP Phase (Days 1-28):** Daily validation of each new component
- **Integration Phase (Weeks 5-8):** Full end-to-end validation on test machine
- **Production Migration (Post-MVP):** Real infrastructure deployment validation

---

## CLI Developer Tool / Infrastructure Management System Specific Requirements

**CLI Interface Requirements:**

- **Command Structure**
  - Clear, consistent verb-noun pattern: `arda [command] [resource] [options]`
  - Comprehensive help system: `arda help` and `arda [command] --help`
  - Tab completion for commands, resources, and arguments
  - Colored output for better readability and status indication

- **Workflow Abstractions**
  - Installation: Single `nix run` command to bootstrap entire environment
  - Machine lifecycle: `create`, `install`, `update`, `remove` workflows
  - Configuration: Generate and update configurations without direct file editing
  - Status reporting: Clear success/failure states with actionable error messages

- **Development Experience**
  - `nix develop` provides shell with arda-cli pre-configured
  - Fast feedback loops for testing changes
  - Non-destructive operations where possible (preview before apply)

**Infrastructure-Specific Requirements:**

- **Multi-Machine Orchestration**
  - Support for 1-10 machines in single repository
  - Declarative machine definitions in arda.nix
  - Per-machine configuration overrides
  - Bulk operations (install to all machines, update all configs)

- **Configuration Management**
  - Declarative state: Configuration matches declared arda.nix exactly
  - Idempotent operations: Running same command multiple times produces same result
  - Configuration validation before deployment
  - Drift detection and reporting

- **Integration with NixOS Ecosystem**
  - Full flake.nix integration and management
  - nixosModule compatibility for existing configurations
  - Nix language evaluation for dynamic configurations
  - Channel and flake update management

- **Secret Management Priority** (Critical Path)
  - Zero-knowledge operations (no secrets in CLI output or logs)
  - Automatic encryption via sops-nix
  - Age key distribution and rotation
  - Machine-specific secret scoping
  - Integration with role-based access patterns

- **Template System**
  - Pre-defined templates for common patterns
  - Template variable substitution
  - Custom template creation and sharing
  - Disk layout templates (ZFS, ext4, etc.)
  - Service configuration templates

**Architecture & Patterns:**

- **Service/Feature/Role Hierarchy** (Core Differentiator)
  - Services: Atomic, tested building blocks (e.g., postgresql, nginx)
  - Features: Composable service combinations (e.g., caching = attic + postgres + minio)
  - Roles: Machine-level assignments combining multiple features
  - Clear separation: Users assign roles, not individual services

- **Minimal Footprint Principle**
  - Aggressive code reduction compared to clan-core
  - Remove features that aren't essential for MVP
  - Opinionated defaults: Pre-configured for common use cases
  - Documentation-first: Every feature must be clearly documented

- **Abstraction Layer Design**
  - arda-core.lib.arda: Main library exposing configuration interface
  - Module system: Users don't need to understand Nix module internals
  - Compatibility layer: Support for clan-style configurations during migration
  - Extensibility: Clean hooks for custom services and features

**Error Handling & Recovery:**

- **Fail-Fast with Clear Recovery Paths**
  - Validate configuration before deployment
  - Specific error messages with suggested fixes
  - Automatic rollback on failed deployments
  - Preserve working state during updates

- **Update Safety**
  - All updates tested in isolation before applying
  - Rollback capability to previous working state
  - Conflict detection before update attempts
  - Manual intervention paths when automatic updates fail

### API Specification

**N/A - CLI Tool (Not an API)**

Arda is a command-line interface tool, not an API service. It does not expose HTTP endpoints or network APIs. All interactions are through CLI commands and local NixOS configuration.

### Authentication & Authorization

**Secret Management via sops-nix**

Arda uses sops-nix for all authentication and secret management needs:

- **Encryption:** All secrets encrypted via age/SOPs before storage
- **Key Distribution:** Age keys distributed securely to authorized machines only
- **Access Control:** Role-based access to secrets (roles determine which secrets machines can access)
- **Rotation:** Support for secret rotation with minimal downtime
- **Audit:** All secret access logged for troubleshooting

**No Traditional Authentication Required:**

- Single-user tool (self-use primary)
- Local machine access assumed for authorized operators
- Git-based access control for repository permissions

{{#if platform_requirements}}

### Platform Support

{{platform_requirements}}
{{/if}}

{{#if device_features}}

### Device Capabilities

{{device_features}}
{{/if}}

{{#if tenant_model}}

### Multi-Tenancy Architecture

{{tenant_model}}
{{/if}}

{{#if permission_matrix}}

### Permissions & Roles

{{permission_matrix}}
{{/if}}
{{/if}}

---

## Functional Requirements

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

---

## Non-Functional Requirements

### Performance

**Operation Efficiency (not runtime performance):**

- **Installation Performance:** Initial `nix run` installation completes in under 1 minute on standard hardware (cold cache). Subsequent installations from cached flakes complete in under 10 seconds.

- **Command Response Time:** All CLI commands (machine create, install, templates apply) complete within 30 seconds on local hardware, with clear progress indicators for longer operations.

- **Update Workflow Efficiency:** `nix flake update` completes in under 2 minutes including validation, with ability to preview changes before applying.

- **Multi-Machine Operations:** Deploy operations can run in parallel across machines with status tracking. Deploying 5 machines should not take more than 10 minutes total (2 minutes per machine max).

**Note:** These are operational efficiency requirements, not computational performance. The focus is on user productivity and task completion time, not system resource consumption.

### Security

**Critical - Secret Management Security:**

- **Encryption Standard:** All secrets encrypted using industry-standard age/SOPs encryption before storage in version control
- **Zero Plaintext Storage:** No secrets stored unencrypted at any point (in memory, disk, or logs)
- **Key Distribution Security:** Age keys distributed only to authorized machines via secure channels
- **Access Control:** Role-based secret access - machines can only access secrets required for their assigned roles
- **Secret Rotation:** Support for secret rotation without exposing plaintext values

**Infrastructure Security:**

- **Deployment Security:** All deployments validate configuration before applying to prevent misconfigurations that could expose services
- **Update Safety:** All updates tested in isolation before production deployment with automatic rollback on failure
- **Configuration Validation:** Prevent deployment of configurations that violate security policies (e.g., exposed ports, weak authentication)

**Operational Security:**

- **Audit Trail:** All configuration changes and deployments logged with timestamps and user identification
- **Recovery:** Ability to rollback to previous working state within 5 minutes of detecting configuration issues
- **No Credentials in Output:** CLI output never contains plaintext secrets, keys, or credentials

### Scalability

**Multi-Machine Scalability:**

- **Machine Count:** Support 1-10 machines efficiently in single repository with clear organization
- **Configuration Scaling:** Single arda.nix configuration can manage 10+ machines with role-based organization
- **Parallel Operations:** Deployments and updates can execute in parallel across multiple machines
- **Resource Efficiency:** Each additional machine adds <100 lines to configuration (composable via roles)

**Repository Scalability:**

- **Decade-Scale Evolution:** Configuration structure remains stable over 10-20 years of evolution
- **Update Conflict Prevention:** Scales to support multiple users updating over time without conflicts
- **Documentation Scaling:** Documentation structure supports adding new services/features without structural changes

**Note:** Arda targets small-scale infrastructure (1-10 machines typical, 50 machines maximum). Not designed for enterprise-scale (100+ machines) deployments.

### Accessibility

**CLI Accessibility & Usability:**

- **Clear Command Structure:** Consistent verb-noun pattern across all commands (`arda [verb] [resource]`)
- **Comprehensive Help:** Every command provides `--help` with examples and common use cases
- **Error Message Quality:** All errors include specific problem description and actionable recovery steps
- **Status Communication:** Clear success/failure indicators with summary of actions taken

**Learning Accessibility (Critical for Educational Goal):**

- **Progressive Complexity:** Simple workflows for basic tasks, advanced options available but not required
- **Documentation Integration:** CLI commands link to relevant documentation sections
- **Example Coverage:** All features include working examples in documentation
- **Beginner-Friendly:** Assumes NixOS familiarity but not deep configuration management experience

**Visual Accessibility:**

- **Color Coding:** Consistent color scheme for success (green), warnings (yellow), errors (red)
- **Structured Output:** Complex information displayed in readable tables and lists
- **Progress Indicators:** Long-running operations show progress with ETA when possible

### Integration

**Nix Ecosystem Integration:**

- **Nix Flakes Compatibility:** Full support for flake.nix workflows, inputs, and updates
- **NixOS Module System:** All configurations usable as standard NixOS modules
- **Nix Language Support:** Dynamic configuration generation using Nix language features
- **Channel Management:** Integration with NixOS channels for base system updates

**Secret Management Integration:**

- **sops-nix Native Integration:** Automatic sops-nix configuration and workflow support
- **age Encryption:** Full age key generation, distribution, and rotation support
- **Multi-Format Secret Support:** Support for various secret formats (SSH keys, API tokens, certificates)

**Version Control Integration:**

- **Git Repository Workflow:** Designed for Git-based version control with proper .gitignore for secrets
- **GitHub Integration:** Template and documentation support for GitHub repository creation
- **Branch Management:** Development workflow supports multiple branches for experimentation

**Platform Integration:**

- **x86_64-linux Primary:** Full support for primary target platform
- **Future Platform Support:** Architecture enables future aarch64-linux and darwin support
- **Cloud-Ready:** Compatible with standard NixOS deployment targets (bare metal, VMs, cloud)

---

## Implementation Planning

### Epic Breakdown Required

Requirements must be decomposed into epics and bite-sized stories (200k context limit).

**Next Step:** Run `workflow epics-stories` to create the implementation breakdown.

---

## References

- Product Brief: bmad-docs/bmm-product-brief-arda-2025-11-14.md

- Architecture: bmad-docs/architecture.md

- Research: No additional research documents provided. Context derived from product brief and existing clan-core architecture analysis.

---

## Next Steps

1. **Epic & Story Breakdown** - Run: `workflow epics-stories`
2. **UX Design** (if UI) - Run: `workflow ux-design`
3. **Architecture** - Run: `workflow create-architecture`

---

*This PRD captures the essence of clan-core - Arda enables sustainable NixOS infrastructure management through clean abstraction, conflict-free updates via flake pinning, and an innovative Service/Feature/Role hierarchy that composes infrastructure from reusable, tested building blocks. Designed for decades-long evolution while maintaining user customizations.*

*Created through collaborative discovery between Lord and AI facilitator.*
