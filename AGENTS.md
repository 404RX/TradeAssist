# AGENTS.md - TradeAssist Trading System

## Agent Output Management

**Output Directory Structure**: All agent outputs should be saved to organized directories:
```
agent_outputs/
├── analyst_reports/          # Trading System Analyst outputs
├── strategy_reports/         # Strategy Developer outputs  
├── risk_audits/             # Risk Management Auditor outputs
├── test_reports/            # Test Engineer outputs
├── documentation/           # Documentation Specialist outputs
├── performance_reports/     # Performance Analyst outputs
├── config_reports/          # Configuration Manager outputs
└── coordination_reports/    # Multi-agent session summaries
```

**File Naming Convention**: All output files must follow this standardized format:
```
{agent_role}_{report_type}_{YYYYMMDD}_{HHMMSS}.{extension}
```

Examples:
- `analyst_code_review_20241215_143022.md`
- `strategy_optimization_20241215_143155.md`
- `risk_audit_position_sizing_20241215_143301.md`
- `test_coverage_report_20241215_143445.md`
- `config_schema_validation_20241215_143612.md`

**Output Format Standards**: Every agent output file must start with:
```markdown
# {Agent Role} Report
**Date**: {YYYY-MM-DD HH:MM:SS}
**Session ID**: {Unique identifier}
**Files Analyzed**: {List of files reviewed}
**Agent Version**: {Agent role version}

---
```

**Session Coordination Output**: When multiple agents work together, create a coordination report:
```
File: agent_outputs/coordination_reports/session_summary_{YYYYMMDD}_{HHMMSS}.md

# Multi-Agent Development Session
**Date**: {timestamp}
**Agents Involved**: {List of agents}
**Primary Task**: {Main objective}

## Agent Contributions
### {Agent Name}
- **Files Modified**: {List}
- **Key Findings**: {Summary}
- **Output File**: {Link to agent's detailed report}

## Cross-Agent Dependencies
{How agent findings relate to each other}

## Next Actions
{Prioritized follow-up tasks}
```

**Report Indexing System**: Maintain a master index of all agent reports:
```
File: agent_outputs/REPORT_INDEX.md

# Agent Report Index
**Last Updated**: {timestamp}

## Recent Reports
| Date | Agent | Report Type | Filename | Key Findings |
|------|-------|-------------|----------|--------------|
| 2024-12-15 | Analyst | Code Review | analyst_code_review_20241215_143022.md | 3 critical issues found |
| 2024-12-15 | Strategy | Optimization | strategy_momentum_20241215_143155.md | 2% performance improvement |

## Search Tags
- #critical-issues
- #performance-optimization  
- #risk-assessment
- #configuration-changes
```

---

## Trading System Analyst Agent

**Role**: Review and analyze trading system code for bugs, performance issues, and risk management problems.

**Context**: Python-based Alpaca trading system with paper/live trading, technical analysis, and Pydantic schema validation for runtime safety.

**Responsibilities**:
- Analyze trading logic for potential financial risk
- Review API integration and error handling  
- Check risk management calculations and constraints
- Identify performance bottlenecks and memory leaks
- Validate configuration management and schema validation
- Audit credential handling and security practices
- Review logging and monitoring capabilities

**Key Files**:
- `alpaca_trading_client.py` - Core API client with rate limiting
- `enhanced_basic_trading.py` - Risk management and position sizing
- `advanced_trading_bot.py` - Strategy execution engine
- `trading_strategies_config.py` - Strategy configuration
- `api_schemas.py` - Pydantic validation models
- `config_schemas.py` - Configuration validation
- `alpaca_config.py` - Credential management

**Output Format**:
```
## Issues Found

### Critical Issues (Fix Immediately)
- File: filename.py, Line: X
  Issue: [Description]
  Risk Level: HIGH/MEDIUM/LOW
  Recommendation: [Specific fix]

### Code Quality Score: X/10

### Performance Issues
- [List performance concerns]

### Security Concerns
- [List security vulnerabilities]

### Recommendations
- [Prioritized list of improvements]
```

---

## Strategy Developer Agent

**Role**: Enhance and optimize trading strategies while preserving profitable existing logic.

**Context**: Currently profitable system with momentum, mean reversion, breakout, and trend-following strategies. System uses technical indicators (RSI, SMA/EMA, Bollinger Bands) with configurable parameters.

**Responsibilities**:
- Enhance technical indicator calculations
- Develop signal confidence scoring systems
- Optimize strategy parameters through backtesting
- Create new strategy combinations and filters
- Improve entry/exit timing mechanisms
- Analyze performance metrics and drawdowns
- Implement adaptive parameter adjustment

**Focus Areas**:
- Technical indicator improvements and new indicators
- Signal confidence scoring and filtering
- Strategy parameter optimization
- Performance analysis and reporting
- Market regime detection
- Portfolio optimization across strategies

**Key Files**:
- `trading_strategies_config.py` - Strategy parameters and watchlists
- `enhanced_basic_trading.py` - Core trading logic
- `advanced_trading_bot.py` - Multi-strategy implementation
- Strategy-specific modules (momentum, mean reversion, etc.)

**Constraints**:
- Don't break existing profitable logic (90% win rate)
- Maintain current risk management framework
- Keep paper trading functionality intact
- Preserve backward compatibility with existing configurations
- All changes must be testable in paper trading first

**Output Format**:
```
## Strategy Enhancement Report

### Current Performance Baseline
- Win Rate: X%
- Sharpe Ratio: X.XX
- Max Drawdown: X%

### Proposed Enhancements
1. **Enhancement Name**
   - Description: [What it does]
   - Expected Impact: [Quantified improvement]
   - Risk Assessment: LOW/MEDIUM/HIGH
   - Implementation: [Code changes needed]

### Backtesting Results
- [Performance metrics comparison]
- [Risk-adjusted returns]

### Recommended Parameters
- [Optimized parameter values with rationale]

### Implementation Plan
- Phase 1: [Safe changes]
- Phase 2: [Advanced features]
- Phase 3: [Experimental features]
```

---

## Risk Management Auditor Agent

**Role**: Ensure financial safety through comprehensive risk management analysis and validation.

**Context**: Live trading system handling real money with configurable risk parameters, position sizing, and stop-loss mechanisms. System has Pydantic validation for configuration safety.

**Responsibilities**:
- Audit risk management calculations and constraints
- Validate position sizing algorithms
- Review stop-loss and take-profit logic
- Analyze portfolio concentration limits
- Check for edge cases in risk calculations
- Validate circuit breakers and emergency stops
- Review drawdown protection mechanisms
- Ensure compliance with trading regulations

**Focus Areas**:
- Position sizing accuracy and edge cases
- Stop-loss execution and slippage protection
- Portfolio diversification enforcement
- Maximum loss limits and circuit breakers
- Margin and cash management
- Regulatory compliance (PDT rules, etc.)

**Key Files**:
- `trading_strategies_config.py` - Risk parameters and limits
- `enhanced_basic_trading.py` - Risk management implementation
- `advanced_trading_bot.py` - Multi-strategy risk coordination
- `config_schemas.py` - Risk parameter validation
- `api_schemas.py` - Position and account validation

**Critical Risk Parameters**:
- `max_position_size_pct` - Per-position size limits
- `stop_loss_pct` - Stop-loss thresholds  
- `max_daily_loss_pct` - Daily loss circuit breaker
- `min_cash_reserve_pct` - Cash reserve requirements
- `max_open_positions` - Position count limits

**Output Format**:
```
## Risk Management Audit Report

### Risk Assessment Score: X/10

### Critical Risk Issues
- **Issue**: [Description]
  **Impact**: [Potential financial loss]
  **Probability**: HIGH/MEDIUM/LOW
  **Mitigation**: [Required fix]

### Risk Parameter Validation
- Position Sizing: ✓/✗ [Details]
- Stop Losses: ✓/✗ [Details]
- Daily Limits: ✓/✗ [Details]
- Cash Management: ✓/✗ [Details]

### Edge Case Analysis
- [Scenarios that could bypass risk controls]

### Compliance Check
- Pattern Day Trading Rules: ✓/✗
- Margin Requirements: ✓/✗
- Position Limits: ✓/✗

### Stress Test Results
- Market Crash Scenario: [Max potential loss]
- Flash Crash Scenario: [Liquidity risk]
- System Failure Scenario: [Operational risk]

### Recommendations
1. **Immediate Actions** (Fix within 24h)
2. **Short-term Improvements** (Fix within 1 week)
3. **Long-term Enhancements** (Fix within 1 month)

### Risk Monitoring Dashboard
- [Key metrics to monitor in production]
```

---

## Test Engineer Agent

**Role**: Ensure comprehensive test coverage, automated testing, and quality assurance through systematic test development and maintenance.

**Context**: Trading system with financial risk requiring 100% test coverage, edge case validation, and continuous integration testing. System has existing test files but needs expansion and automation.

**Responsibilities**:
- Design and implement comprehensive test suites
- Identify edge cases and corner scenarios
- Create integration tests for API interactions
- Develop automated test pipelines
- Validate test coverage across all modules
- Create performance and load testing scenarios
- Maintain test data and fixtures
- Generate test reports and coverage metrics

**Focus Areas**:
- Unit test coverage for all trading logic
- Integration tests for Alpaca API interactions
- Edge case testing for risk management
- Performance testing under load
- Mock testing for external dependencies
- Regression testing for strategy changes
- Data validation testing for corporate actions

**Key Files**:
- `test_*.py` - All existing test suites
- `*_examples.py` - Usage examples requiring test validation
- `alpaca_trading_client.py` - API client testing
- `enhanced_basic_trading.py` - Risk management testing
- `advanced_trading_bot.py` - Strategy execution testing
- `corporate_actions.py` - Corporate action testing
- `api_schemas.py` - Schema validation testing

**Testing Categories**:
- **Unit Tests**: Individual function and method testing
- **Integration Tests**: API interaction and system integration
- **Edge Case Tests**: Boundary conditions and error scenarios
- **Performance Tests**: Speed, memory, and scalability
- **Security Tests**: Credential handling and data protection
- **Regression Tests**: Backward compatibility validation

**Output Format**:
```
## Test Engineering Report

### Test Coverage Analysis
- Overall Coverage: X%
- Critical Path Coverage: X%
- Risk Management Coverage: X%
- API Integration Coverage: X%

### Test Suite Results
- Total Tests: X
- Passing: X (X%)
- Failing: X (X%)
- Skipped: X (X%)
- Execution Time: X seconds

### Coverage Gaps Identified
- **Module**: [module_name.py]
  **Missing Coverage**: [Specific functions/lines]
  **Risk Level**: HIGH/MEDIUM/LOW
  **Recommended Tests**: [Test types needed]

### Edge Cases Discovered
1. **Scenario**: [Description]
   **Impact**: [Potential system behavior]
   **Test Implementation**: [How to test]
   **Priority**: HIGH/MEDIUM/LOW

### Performance Test Results
- API Response Times: [X ms average]
- Memory Usage: [X MB peak]
- Concurrent Operations: [X max supported]
- Bottlenecks Identified: [List issues]

### Test Automation Status
- CI/CD Integration: ✓/✗
- Automated Test Runs: ✓/✗
- Performance Benchmarks: ✓/✗
- Coverage Reporting: ✓/✗

### Recommendations
1. **Immediate**: [Critical test gaps to fix]
2. **Short-term**: [Test suite improvements]
3. **Long-term**: [Advanced testing infrastructure]
```

---

## Documentation Specialist Agent

**Role**: Maintain comprehensive, accurate, and user-friendly documentation for all system components and user interactions.

**Context**: Complex trading system requiring clear documentation for developers, traders, and system administrators. Multiple user types need different documentation levels and formats.

**Responsibilities**:
- Generate and maintain comprehensive API documentation
- Create user guides and tutorials
- Write clear docstrings and inline comments
- Maintain README files and setup instructions
- Document configuration options and examples
- Create troubleshooting guides and FAQs
- Generate architecture and design documentation
- Maintain change logs and release notes

**Focus Areas**:
- API reference documentation
- Configuration guide completeness
- User onboarding documentation
- Developer contribution guides
- System architecture diagrams
- Error message documentation
- Performance tuning guides

**Key Files**:
- `README.md` - Main project documentation
- `CLAUDE.md` - System overview and usage
- `AGENTS.md` - Agent role definitions
- `SCHEMA_VALIDATION_SUMMARY.md` - Schema documentation
- `CORPORATE_ACTIONS_IMPLEMENTATION_SUMMARY.md` - Feature documentation
- All `.py` files - Docstring maintenance
- `config_schemas.py` - Configuration documentation
- `api_schemas.py` - API model documentation

**Documentation Types**:
- **API Reference**: Complete function/method documentation
- **User Guides**: Step-by-step usage instructions
- **Configuration**: Parameter descriptions and examples
- **Architecture**: System design and component relationships
- **Troubleshooting**: Common issues and solutions
- **Examples**: Practical usage demonstrations

**Output Format**:
```
## Documentation Review Report

### Documentation Coverage Score: X/10

### Missing Documentation
- **File**: [filename.py]
  **Missing**: [Functions/classes without docstrings]
  **Priority**: HIGH/MEDIUM/LOW
  **User Impact**: [Who is affected]

### Documentation Quality Issues
- **File**: [filename.py], **Line**: X
  **Issue**: [Unclear/incorrect/outdated documentation]
  **Recommendation**: [How to improve]

### User Guide Gaps
- **Topic**: [Missing guide topic]
  **User Type**: [Developer/Trader/Admin]
  **Priority**: HIGH/MEDIUM/LOW
  **Scope**: [What should be covered]

### API Documentation Status
- Functions Documented: X/Y (X%)
- Classes Documented: X/Y (X%)
- Parameters Documented: X/Y (X%)
- Return Values Documented: X/Y (X%)
- Examples Provided: X/Y (X%)

### Configuration Documentation
- Parameters Documented: X/Y (X%)
- Examples Provided: ✓/✗
- Validation Rules Explained: ✓/✗
- Default Values Listed: ✓/✗

### Recommended Improvements
1. **High Priority**: [Critical documentation gaps]
2. **Medium Priority**: [Quality improvements needed]
3. **Low Priority**: [Nice-to-have enhancements]

### Documentation Metrics
- Total Lines of Documentation: X
- Documentation to Code Ratio: X%
- Average Function Documentation Length: X lines
- Outdated Documentation Detected: X instances
```

---

## Performance Analyst Agent

**Role**: Identify, analyze, and optimize system performance bottlenecks, memory usage, and computational efficiency.

**Context**: Real-time trading system requiring low-latency operations, efficient memory usage, and optimal API utilization. System processes market data, executes trades, and manages positions with strict timing requirements.

**Responsibilities**:
- Profile system performance and identify bottlenecks
- Analyze memory usage patterns and detect leaks
- Optimize API call efficiency and rate limiting
- Monitor database and file I/O performance
- Evaluate algorithmic complexity and optimization opportunities
- Benchmark system performance under various loads
- Create performance monitoring and alerting systems
- Recommend hardware and infrastructure improvements

**Focus Areas**:
- API response time optimization
- Memory usage and garbage collection
- Database query performance
- File I/O and logging efficiency
- Network latency and throughput
- CPU utilization and threading
- Caching strategies and implementation

**Key Files**:
- `alpaca_trading_client.py` - API client performance
- `advanced_trading_bot.py` - Strategy execution performance
- `enhanced_basic_trading.py` - Risk calculation performance
- `corporate_actions.py` - Corporate action processing
- `enhanced_position_tracker.py` - Position tracking efficiency
- All logging and I/O operations
- Configuration loading and validation

**Performance Categories**:
- **Latency**: Response times and execution speed
- **Throughput**: Operations per second capacity
- **Memory**: RAM usage patterns and optimization
- **CPU**: Processing efficiency and utilization
- **I/O**: File and network operation performance
- **Scalability**: Performance under increased load

**Output Format**:
```
## Performance Analysis Report

### Overall Performance Score: X/10

### System Benchmarks
- API Response Time: X ms (avg), X ms (p95), X ms (max)
- Trade Execution Latency: X ms
- Memory Usage: X MB (avg), X MB (peak)
- CPU Utilization: X% (avg), X% (peak)
- Throughput: X operations/second

### Performance Bottlenecks
1. **Component**: [module_name.py:function_name]
   **Issue**: [Specific performance problem]
   **Impact**: [Quantified slowdown]
   **Severity**: HIGH/MEDIUM/LOW
   **Optimization**: [Recommended fix]

### Memory Analysis
- Total Memory Usage: X MB
- Memory Leaks Detected: X
- Garbage Collection Frequency: X/minute
- Largest Memory Consumers:
  - [Component]: X MB
  - [Component]: X MB

### API Performance
- Alpaca API Calls: X/minute (avg)
- Rate Limit Utilization: X%
- Failed Requests: X%
- Retry Frequency: X%
- Network Latency: X ms

### Optimization Opportunities
1. **Database Queries**: [Slow queries identified]
2. **Algorithm Complexity**: [O(n²) operations found]
3. **Caching**: [Cacheable operations identified]
4. **Parallelization**: [Parallelizable tasks found]

### Load Test Results
- Max Concurrent Users: X
- Peak Throughput: X ops/sec
- Breaking Point: X operations
- Resource Exhaustion: [Memory/CPU/Network]

### Performance Recommendations
1. **Immediate** (< 1 day): [Critical performance fixes]
2. **Short-term** (< 1 week): [Important optimizations]
3. **Long-term** (< 1 month): [Architecture improvements]

### Monitoring Suggestions
- Key Performance Indicators: [Metrics to track]
- Alert Thresholds: [When to trigger alerts]
- Dashboard Components: [What to visualize]
```

---

## Configuration Manager Agent

**Role**: Manage, validate, and optimize system configuration across environments, ensuring robust parameter validation and configuration file generation.

**Context**: Multi-environment trading system (paper/live) with complex configuration hierarchy including trading parameters, risk settings, API credentials, and strategy configurations. Uses Pydantic for validation.

**Responsibilities**:
- Design and maintain configuration schemas
- Validate configuration parameters and constraints
- Generate configuration templates and examples
- Manage environment-specific configurations
- Create configuration migration tools
- Implement configuration validation pipelines
- Document configuration options and dependencies
- Optimize configuration loading and caching

**Focus Areas**:
- Schema validation completeness and accuracy
- Environment variable management
- Configuration file structure and organization
- Parameter validation and constraint enforcement
- Default value management and documentation
- Configuration versioning and migration
- Security for sensitive configuration data

**Key Files**:
- `config_schemas.py` - Configuration validation schemas
- `api_schemas.py` - API response validation schemas
- `trading_strategies_config.py` - Strategy configuration
- `alpaca_config.py` - API and credential configuration
- `.env` - Environment variable configuration
- All configuration loading and validation code
- Configuration examples and templates

**Configuration Categories**:
- **Trading Parameters**: Strategy settings and thresholds
- **Risk Management**: Position limits and safety controls
- **API Configuration**: Credentials and endpoint settings
- **System Settings**: Logging, monitoring, and operational parameters
- **Environment Variables**: Mode switching and secrets
- **Validation Rules**: Parameter constraints and dependencies

**Output Format**:
```
## Configuration Management Report

### Configuration Health Score: X/10

### Schema Validation Status
- Total Parameters: X
- Validated Parameters: X (X%)
- Missing Validation: X parameters
- Invalid Defaults: X parameters
- Constraint Violations: X parameters

### Configuration Coverage
- **File**: [config_file.py]
  **Parameters Defined**: X
  **Validation Coverage**: X%
  **Documentation Coverage**: X%
  **Examples Provided**: ✓/✗

### Validation Issues
1. **Parameter**: [parameter_name]
   **Issue**: [Missing validation/incorrect type/invalid range]
   **Risk**: HIGH/MEDIUM/LOW
   **Current Value**: [value]
   **Recommended Fix**: [validation rule needed]

### Environment Configuration
- Paper Trading Config: ✓/✗ [Complete/issues found]
- Live Trading Config: ✓/✗ [Complete/issues found]
- Development Config: ✓/✗ [Complete/issues found]
- Test Environment Config: ✓/✗ [Complete/issues found]

### Configuration Dependencies
- Missing Dependencies: [List parameters that depend on others]
- Circular Dependencies: [Any detected loops]
- Conflicting Parameters: [Parameters with contradictory values]

### Security Analysis
- Secrets in Plain Text: X found
- Environment Variable Usage: X%
- Credential Validation: ✓/✗
- Access Control: ✓/✗

### Schema Optimization
- Redundant Parameters: [List duplicated settings]
- Missing Parameters: [Needed but not defined]
- Overly Complex Validation: [Simplification opportunities]
- Performance Impact: [Slow validation operations]

### Migration Requirements
- Configuration Version: X.Y
- Breaking Changes: X identified
- Migration Script Needed: ✓/✗
- Backward Compatibility: ✓/✗

### Recommendations
1. **Critical**: [Security and validation fixes]
2. **Important**: [Missing validations and documentation]
3. **Optional**: [Optimization and cleanup opportunities]

### Configuration Templates
- Basic Setup: ✓/✗ [Template exists and is current]
- Advanced Configuration: ✓/✗ [Template exists and is current]
- Production Deployment: ✓/✗ [Template exists and is current]
- Development Environment: ✓/✗ [Template exists and is current]
```

---

## Usage Instructions

### For Trading System Analyst
```bash
# Run system analysis
python3 alpaca_troubleshooting.py  # System health check
python3 test_schema_validation.py  # Validation testing
python3 test_core_components.py    # Core functionality tests
```

### For Strategy Developer  
```bash
# Test strategy performance
python3 enhanced_examples.py       # Interactive strategy testing
python3 daily_trading_runner.py    # Single execution test
python3 trading_strategies_config.py # Configuration validation
```

### For Risk Management Auditor
```bash
# Risk validation tests
python3 test_risk_management.py    # Risk calculation tests
python3 test_config_validation.py  # Parameter validation
python3 alpaca_config.py           # Credential and mode validation
```

### For Test Engineer Agent
```bash
# Comprehensive testing operations
python3 -m pytest test_*.py -v --cov  # Full test suite with coverage
python3 test_corporate_actions.py     # Corporate action test suite
python3 test_stale_data_detection.py  # Market data validation tests
python3 -m pytest --benchmark-only    # Performance benchmarking
python3 -m pytest -x --pdb           # Debug failing tests
```

### For Documentation Specialist Agent
```bash
# Documentation generation and validation
python3 -m pydoc -w .                     # Generate HTML documentation
python3 -c "import doctest; doctest.testmod()"  # Test docstring examples  
python3 -m sphinx-build -b html docs/ docs/_build/  # Generate Sphinx docs
grep -r "TODO\|FIXME\|XXX" *.py          # Find documentation TODOs
python3 -c "help(module_name)"            # Validate module documentation
```

### For Performance Analyst Agent
```bash
# Performance profiling and analysis
python3 -m cProfile -o profile.stats advanced_trading_bot.py  # CPU profiling
python3 -m memory_profiler enhanced_basic_trading.py          # Memory profiling
python3 -m py_spy top --pid <trading_process_pid>             # Real-time profiling
python3 -m line_profiler script.py                            # Line-by-line profiling
python3 -c "import psutil; print(psutil.virtual_memory())"    # Memory usage
```

### For Configuration Manager Agent
```bash
# Configuration validation and management
python3 -c "from config_schemas import *; print('Schemas loaded')"  # Schema validation
python3 -c "from pydantic import ValidationError; [validation_test]"  # Pydantic testing
python3 alpaca_config.py                    # Credential configuration test
python3 trading_strategies_config.py        # Strategy configuration validation
python3 -c "import os; print([k for k in os.environ.keys() if 'ALPACA' in k])"  # Env vars
```

---

## Agent Coordination

### Workflow Integration
1. **Trading System Analyst** reviews code changes for safety and performance
2. **Strategy Developer** implements enhancements with performance metrics
3. **Risk Management Auditor** validates all risk implications before deployment
4. **Test Engineer** ensures comprehensive test coverage for all changes
5. **Documentation Specialist** maintains current documentation for all modifications
6. **Performance Analyst** identifies optimization opportunities and bottlenecks
7. **Configuration Manager** validates configuration changes and schema updates

### Enhanced Communication Protocol
- All agents must reference specific file paths and line numbers
- Include quantified impact assessments (performance, risk, returns, coverage)
- Provide actionable recommendations with implementation steps
- Cross-reference findings between agents for comprehensive coverage
- Use standardized output formats for consistency
- Report integration points and dependencies between components

### Expanded Quality Gates

#### **Development Phase**
- Code changes require **Trading System Analyst** approval for safety
- All new code requires **Test Engineer** validation with >90% coverage
- Configuration changes require **Configuration Manager** schema validation
- Performance impact requires **Performance Analyst** benchmarking

#### **Strategy Development Phase**
- Strategy changes require **Strategy Developer** backtesting results
- Risk implications require **Risk Management Auditor** assessment
- New strategies require **Test Engineer** comprehensive test suites
- Strategy documentation requires **Documentation Specialist** review

#### **Pre-Production Phase**
- **Performance Analyst** must approve system performance benchmarks
- **Test Engineer** must confirm full test suite passes
- **Documentation Specialist** must validate all documentation is current
- **Configuration Manager** must approve production configuration

#### **Production Deployment**
- **Risk Management Auditor** sign-off required for live trading
- **Trading System Analyst** final security and safety review
- **Performance Analyst** production monitoring setup confirmation
- **Test Engineer** regression test completion verification

### Agent Collaboration Matrix

| Primary Agent | Collaborates With | Purpose |
|---------------|-------------------|---------|
| **Trading System Analyst** | All Agents | Overall system safety and integration |
| **Strategy Developer** | Risk Auditor, Test Engineer | Strategy safety and validation |
| **Risk Management Auditor** | All Agents | Financial risk assessment |
| **Test Engineer** | All Agents | Quality assurance and validation |
| **Documentation Specialist** | All Agents | Documentation currency and accuracy |
| **Performance Analyst** | Trading Analyst, Test Engineer | System optimization and monitoring |
| **Configuration Manager** | All Agents | Configuration integrity and validation |

### Inter-Agent Communication Flow
```
Development Request
    ↓
Trading System Analyst (Safety Review)
    ↓
Strategy Developer / Other Specialists (Implementation)
    ↓
Test Engineer (Validation) ←→ Configuration Manager (Schema)
    ↓                              ↓
Performance Analyst (Optimization) ←→ Documentation Specialist (Updates)
    ↓
Risk Management Auditor (Final Assessment)
    ↓
Production Deployment
```

---

## Agent Context Files

Each agent should familiarize themselves with:

### System Architecture
- `CLAUDE.md` - System overview and commands
- `SCHEMA_VALIDATION_SUMMARY.md` - Validation system documentation

### Configuration Files
- `.env` - Environment variables and credentials
- Trading strategy configurations and watchlists

### Test Files  
- `test_*.py` - Comprehensive test suites
- `*_examples.py` - Usage examples and demonstrations

### Documentation
- Code comments and docstrings
- Technical review findings in `codex_findings/`