"""
Rigorous A/B Testing Framework with Statistical Analysis

Implements statistical hypothesis testing for AI model comparisons,
feature experiments, and compliance effectiveness measurements.
Includes t-tests, chi-squared tests, and comprehensive experiment management.
"""

import hashlib
import numpy as np
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4
from scipy import stats
from scipy.stats import ttest_ind, chi2_contingency, mannwhitneyu

from config.logging_config import get_logger
from .analytics_monitor import MetricEvent, MetricType, get_analytics_monitor

logger = get_logger(__name__)


class ExperimentType(Enum):
    """Types of A/B experiments."""

    AI_MODEL_COMPARISON = "ai_model_comparison"
    PROMPT_OPTIMIZATION = "prompt_optimization"
    FEATURE_ROLLOUT = "feature_rollout"
    UI_OPTIMIZATION = "ui_optimization"
    COMPLIANCE_EFFECTIVENESS = "compliance_effectiveness"
    ASSESSMENT_METHODOLOGY = "assessment_methodology"

    # MetricType imported from analytics_monitor above
    CATEGORICAL = "categorical"  # User preferences, status categories
    COUNT = "count"  # Number of actions, events


class StatisticalTest(Enum):
    """Available statistical tests."""

    T_TEST = "t_test"  # Two-sample t-test for continuous metrics
    WELCH_T_TEST = "welch_t_test"  # Welch's t-test (unequal variances)
    CHI_SQUARED = "chi_squared"  # Chi-squared test for categorical data
    MANN_WHITNEY = "mann_whitney"  # Non-parametric alternative to t-test
    KOLMOGOROV_SMIRNOV = "ks_test"  # Distribution comparison
    FISHER_EXACT = "fisher_exact"  # Exact test for small samples


class ExperimentStatus(Enum):
    """Experiment lifecycle status."""

    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


@dataclass
class ExperimentConfig:
    """Configuration for an A/B experiment."""

    name: str
    description: str
    experiment_type: ExperimentType
    metric_type: MetricType
    primary_metric: str
    secondary_metrics: List[str] = field(default_factory=list)

    # Statistical parameters
    significance_level: float = 0.05  # Alpha (Type I error rate)
    power: float = 0.8  # 1 - Beta (Type II error rate)
    min_effect_size: float = 0.1  # Minimum detectable effect

    # Experiment design
    traffic_split: Dict[str, float] = field(
        default_factory=lambda: {"control": 0.5, "treatment": 0.5}
    )
    stratification_keys: List[str] = field(default_factory=list)  # User segments, regions, etc.

    # Duration and sample size
    min_sample_size: int = 100
    max_duration_days: int = 30
    early_stopping_enabled: bool = True

    # Metadata
    owner: str = "system"
    tags: List[str] = field(default_factory=list)


@dataclass
class StatisticalResult:
    """Results of statistical test analysis."""

    test_name: str
    statistic: float
    p_value: float
    confidence_interval: Optional[Tuple[float, float]]
    effect_size: float
    power: float

    # Interpretation
    is_significant: bool
    practical_significance: bool
    recommendation: str

    # Additional metrics
    sample_sizes: Dict[str, int]
    means: Dict[str, float]
    std_devs: Dict[str, float]

    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentData:
    """Data point in an A/B experiment."""

    experiment_id: str
    variant: str  # "control", "treatment", "variant_a", etc.
    user_id: str
    session_id: Optional[str]
    timestamp: datetime

    # Metric values
    primary_metric_value: Union[float, int, str, bool]
    secondary_metrics: Dict[str, Union[float, int, str, bool]] = field(default_factory=dict)

    # Context
    user_segments: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ABTestingFramework:
    """Comprehensive A/B Testing Framework with rigorous statistical analysis."""

    def __init__(self) -> None:
        """Initialize the A/B testing framework."""
        self.experiments: Dict[str, ExperimentConfig] = {}
        self.experiment_data: Dict[str, List[ExperimentData]] = {}
        self.experiment_status: Dict[str, ExperimentStatus] = {}
        self.experiment_results: Dict[str, List[StatisticalResult]] = {}

        # Analytics integration
        self.analytics_monitor = get_analytics_monitor()

        # Statistical configuration
        self.confidence_levels = [0.90, 0.95, 0.99]
        self.effect_size_thresholds = {"small": 0.2, "medium": 0.5, "large": 0.8}

    def create_experiment(self, config: ExperimentConfig) -> str:
        """
        Create a new A/B experiment.

        Args:
            config: Experiment configuration

        Returns:
            Experiment ID
        """
        experiment_id = str(uuid4())

        # Validate configuration
        self._validate_experiment_config(config)

        # Calculate required sample size
        required_sample_size = self._calculate_sample_size(config)
        if config.min_sample_size < required_sample_size:
            logger.warning(
                f"Configured sample size ({config.min_sample_size}) is below "
                f"statistically required size ({required_sample_size})"
            )

        # Store experiment
        self.experiments[experiment_id] = config
        self.experiment_data[experiment_id] = []
        self.experiment_status[experiment_id] = ExperimentStatus.DRAFT
        self.experiment_results[experiment_id] = []

        logger.info(f"Created experiment {experiment_id}: {config.name}")

        # Record analytics
        self.analytics_monitor.record_metric(
            MetricEvent(
                timestamp=datetime.now(),
                metric_type=MetricType.USAGE,
                name="experiment_created",
                value=1.0,
                metadata={
                    "experiment_id": experiment_id,
                    "experiment_type": config.experiment_type.value,
                    "metric_type": config.metric_type.value,
                },
            )
        )

        return experiment_id

    def start_experiment(self, experiment_id: str) -> bool:
        """
        Start an experiment.

        Args:
            experiment_id: ID of experiment to start

        Returns:
            True if started successfully
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        if self.experiment_status[experiment_id] != ExperimentStatus.DRAFT:
            raise ValueError(f"Experiment {experiment_id} is not in draft status")

        self.experiment_status[experiment_id] = ExperimentStatus.RUNNING

        logger.info(f"Started experiment {experiment_id}")

        # Record analytics
        self.analytics_monitor.record_metric(
            MetricEvent(
                timestamp=datetime.now(),
                metric_type=MetricType.USAGE,
                name="experiment_started",
                value=1.0,
                metadata={"experiment_id": experiment_id},
            )
        )

        return True

    def assign_variant(
        self, experiment_id: str, user_id: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Assign a user to an experiment variant.

        Args:
            experiment_id: ID of the experiment
            user_id: User identifier
            context: Additional context for stratification

        Returns:
            Assigned variant name
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        if self.experiment_status[experiment_id] != ExperimentStatus.RUNNING:
            logger.warning(f"Experiment {experiment_id} is not running")
            return "control"  # Default to control if experiment not running

        config = self.experiments[experiment_id]

        # Deterministic assignment based on user ID and experiment ID
        hash_input = f"{experiment_id}:{user_id}"

        # Add stratification if configured
        if config.stratification_keys and context:
            strata_values = [str(context.get(key, "unknown")) for key in config.stratification_keys]
            hash_input += ":" + ":".join(strata_values)

        # Generate hash and convert to assignment
        hash_value = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
        assignment_ratio = (hash_value % 10000) / 10000.0

        # Assign to variant based on traffic split
        cumulative_probability = 0.0
        for variant, probability in config.traffic_split.items():
            cumulative_probability += probability
            if assignment_ratio <= cumulative_probability:
                return variant

        # Fallback to control
        return "control"

    def record_metric(
        self,
        experiment_id: str,
        variant: str,
        user_id: str,
        primary_metric_value: Union[float, int, str, bool],
        secondary_metrics: Optional[Dict[str, Union[float, int, str, bool]]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Record a metric observation for an experiment.

        Args:
            experiment_id: ID of the experiment
            variant: Variant the user was assigned to
            user_id: User identifier
            primary_metric_value: Value of the primary metric
            secondary_metrics: Values of secondary metrics
            context: Additional context information

        Returns:
            True if recorded successfully
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        data_point = ExperimentData(
            experiment_id=experiment_id,
            variant=variant,
            user_id=user_id,
            session_id=context.get("session_id") if context else None,
            timestamp=datetime.now(),
            primary_metric_value=primary_metric_value,
            secondary_metrics=secondary_metrics or {},
            user_segments=context.get("user_segments", {}) if context else {},
            metadata=context or {},
        )

        self.experiment_data[experiment_id].append(data_point)

        # Record analytics
        self.analytics_monitor.record_metric(
            MetricEvent(
                timestamp=datetime.now(),
                metric_type=MetricType.USAGE,
                name="experiment_metric_recorded",
                value=1.0,
                metadata={
                    "experiment_id": experiment_id,
                    "variant": variant,
                    "metric_value": str(primary_metric_value),
                },
            )
        )

        return True

    def analyze_experiment(
        self, experiment_id: str, confidence_level: float = 0.95
    ) -> StatisticalResult:
        """
        Perform rigorous statistical analysis of an experiment.

        Args:
            experiment_id: ID of the experiment to analyze
            confidence_level: Confidence level for statistical tests

        Returns:
            Statistical analysis results
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        config = self.experiments[experiment_id]
        data = self.experiment_data[experiment_id]

        if len(data) < config.min_sample_size:
            logger.warning(
                f"Insufficient data for analysis: {len(data)} < {config.min_sample_size}"
            )

        # Group data by variant
        variant_data = self._group_data_by_variant(data)

        # Choose appropriate statistical test
        test_type = self._select_statistical_test(config.metric_type, variant_data)

        # Perform statistical analysis
        result = self._perform_statistical_test(test_type, variant_data, config, confidence_level)

        # Store result
        self.experiment_results[experiment_id].append(result)

        # Record analytics
        self.analytics_monitor.record_metric(
            MetricEvent(
                timestamp=datetime.now(),
                metric_type=MetricType.QUALITY,
                name="experiment_analyzed",
                value=result.p_value,
                metadata={
                    "experiment_id": experiment_id,
                    "test_type": result.test_name,
                    "is_significant": result.is_significant,
                    "effect_size": result.effect_size,
                },
            )
        )

        return result

    def _validate_experiment_config(self, config: ExperimentConfig) -> None:
        """Validate experiment configuration."""
        if config.significance_level <= 0 or config.significance_level >= 1:
            raise ValueError("Significance level must be between 0 and 1")

        if config.power <= 0 or config.power >= 1:
            raise ValueError("Power must be between 0 and 1")

        if abs(sum(config.traffic_split.values()) - 1.0) > 1e-6:
            raise ValueError("Traffic split probabilities must sum to 1.0")

        if config.min_sample_size < 10:
            raise ValueError("Minimum sample size should be at least 10")

    def _calculate_sample_size(self, config: ExperimentConfig) -> int:
        """
        Calculate required sample size for adequate statistical power.

        Args:
            config: Experiment configuration

        Returns:
            Required sample size per variant
        """
        alpha = config.significance_level
        beta = 1 - config.power
        effect_size = config.min_effect_size

        # Using Cohen's formula for two-sample t-test
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(1 - beta)

        # Sample size per group
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2

        return max(int(np.ceil(n)), config.min_sample_size)

    def _group_data_by_variant(
        self, data: List[ExperimentData]
    ) -> Dict[str, List[Union[float, int, str, bool]]]:
        """Group experiment data by variant."""
        variant_data = defaultdict(list)

        for data_point in data:
            variant_data[data_point.variant].append(data_point.primary_metric_value)

        return dict(variant_data)

    def _select_statistical_test(
        self, metric_type: MetricType, variant_data: Dict[str, List]
    ) -> StatisticalTest:
        """
        Select appropriate statistical test based on data characteristics.

        Args:
            metric_type: Type of metric being analyzed
            variant_data: Data grouped by variant

        Returns:
            Recommended statistical test
        """
        if metric_type == MetricType.CONTINUOUS:
            # Check for normality and equal variances
            variants = list(variant_data.keys())
            if len(variants) == 2:
                control_data = np.array(variant_data[variants[0]], dtype=float)
                treatment_data = np.array(variant_data[variants[1]], dtype=float)

                # Test for normality (Shapiro-Wilk for small samples, KS for large)
                if len(control_data) < 50 or len(treatment_data) < 50:
                    _, p_control = stats.shapiro(control_data)
                    _, p_treatment = stats.shapiro(treatment_data)
                else:
                    _, p_control = stats.kstest(control_data, "norm")
                    _, p_treatment = stats.kstest(treatment_data, "norm")

                # If data is not normal, use non-parametric test
                if p_control < 0.05 or p_treatment < 0.05:
                    return StatisticalTest.MANN_WHITNEY

                # Test for equal variances
                _, p_var = stats.levene(control_data, treatment_data)

                if p_var < 0.05:
                    return StatisticalTest.WELCH_T_TEST  # Unequal variances
                else:
                    return StatisticalTest.T_TEST  # Equal variances

            return StatisticalTest.T_TEST

        elif metric_type in (MetricType.BINARY, MetricType.CATEGORICAL):
            # Use chi-squared for categorical data
            return StatisticalTest.CHI_SQUARED

        elif metric_type == MetricType.COUNT:
            # Use Mann-Whitney U for count data (often not normally distributed)
            return StatisticalTest.MANN_WHITNEY

        return StatisticalTest.T_TEST  # Default

    def _perform_statistical_test(
        self,
        test_type: StatisticalTest,
        variant_data: Dict[str, List],
        config: ExperimentConfig,
        confidence_level: float,
    ) -> StatisticalResult:
        """
        Perform the specified statistical test.

        Args:
            test_type: Type of statistical test to perform
            variant_data: Data grouped by variant
            config: Experiment configuration
            confidence_level: Confidence level for the test

        Returns:
            Statistical test results
        """
        variants = list(variant_data.keys())
        alpha = 1 - confidence_level

        if len(variants) != 2:
            raise ValueError("Currently only supports two-variant experiments")

        control_data = np.array(variant_data[variants[0]], dtype=float)
        treatment_data = np.array(variant_data[variants[1]], dtype=float)

        # Calculate basic statistics
        control_mean = np.mean(control_data)
        treatment_mean = np.mean(treatment_data)
        control_std = np.std(control_data, ddof=1)
        treatment_std = np.std(treatment_data, ddof=1)

        effect_size = (treatment_mean - control_mean) / np.sqrt(
            (control_std**2 + treatment_std**2) / 2
        )

        # Perform statistical test
        if test_type == StatisticalTest.T_TEST:
            statistic, p_value = ttest_ind(control_data, treatment_data, equal_var=True)
            test_name = "Two-sample t-test (equal variances)"

        elif test_type == StatisticalTest.WELCH_T_TEST:
            statistic, p_value = ttest_ind(control_data, treatment_data, equal_var=False)
            test_name = "Welch's t-test (unequal variances)"

        elif test_type == StatisticalTest.MANN_WHITNEY:
            statistic, p_value = mannwhitneyu(control_data, treatment_data, alternative="two-sided")
            test_name = "Mann-Whitney U test"

        elif test_type == StatisticalTest.CHI_SQUARED:
            # Create contingency table for categorical data
            control_counts = self._get_category_counts(variant_data[variants[0]])
            treatment_counts = self._get_category_counts(variant_data[variants[1]])

            # Align categories
            all_categories = set(control_counts.keys()) | set(treatment_counts.keys())
            contingency_table = []
            for category in all_categories:
                contingency_table.append(
                    [control_counts.get(category, 0), treatment_counts.get(category, 0)]
                )

            chi2, p_value, dof, expected = chi2_contingency(contingency_table)
            statistic = chi2
            test_name = "Chi-squared test"

        else:
            raise ValueError(f"Unsupported test type: {test_type}")

        # Calculate confidence interval for mean difference
        if test_type in [StatisticalTest.T_TEST, StatisticalTest.WELCH_T_TEST]:
            mean_diff = treatment_mean - control_mean
            pooled_se = np.sqrt(
                control_std**2 / len(control_data) + treatment_std**2 / len(treatment_data)
            )

            if test_type == StatisticalTest.T_TEST:
                df = len(control_data) + len(treatment_data) - 2
            else:  # Welch's t-test
                df = (
                    control_std**2 / len(control_data) + treatment_std**2 / len(treatment_data)
                ) ** 2 / (
                    control_std**4 / (len(control_data) ** 2 * (len(control_data) - 1))
                    + treatment_std**4 / (len(treatment_data) ** 2 * (len(treatment_data) - 1))
                )

            t_critical = stats.t.ppf(1 - alpha / 2, df)
            margin_error = t_critical * pooled_se
            confidence_interval = (mean_diff - margin_error, mean_diff + margin_error)
        else:
            confidence_interval = None

        # Calculate statistical power
        observed_effect_size = abs(effect_size)
        power = self._calculate_power(
            observed_effect_size, len(control_data), len(treatment_data), alpha
        )

        # Determine significance
        is_significant = p_value < alpha
        practical_significance = abs(effect_size) >= config.min_effect_size

        # Generate recommendation
        recommendation = self._generate_recommendation(
            is_significant, practical_significance, effect_size, p_value, power
        )

        return StatisticalResult(
            test_name=test_name,
            statistic=statistic,
            p_value=p_value,
            confidence_interval=confidence_interval,
            effect_size=effect_size,
            power=power,
            is_significant=is_significant,
            practical_significance=practical_significance,
            recommendation=recommendation,
            sample_sizes={variants[0]: len(control_data), variants[1]: len(treatment_data)},
            means={variants[0]: control_mean, variants[1]: treatment_mean},
            std_devs={variants[0]: control_std, variants[1]: treatment_std},
            metadata={
                "confidence_level": confidence_level,
                "alpha": alpha,
                "test_type": test_type.value,
            },
        )

    def _get_category_counts(self, data: List) -> Dict[str, int]:
        """Get counts for each category in categorical data."""
        counts = defaultdict(int)
        for value in data:
            counts[str(value)] += 1
        return dict(counts)

    def _calculate_power(self, effect_size: float, n1: int, n2: int, alpha: float) -> float:
        """
        Calculate statistical power for the test.

        Args:
            effect_size: Observed effect size
            n1: Sample size for group 1
            n2: Sample size for group 2
            alpha: Significance level

        Returns:
            Statistical power (1 - beta)
        """
        # For two-sample t-test
        pooled_n = 2 / (1 / n1 + 1 / n2)
        ncp = effect_size * np.sqrt(pooled_n / 2)  # Non-centrality parameter

        t_critical = stats.t.ppf(1 - alpha / 2, n1 + n2 - 2)

        # Power calculation using non-central t-distribution
        power = (
            1
            - stats.nct.cdf(t_critical, n1 + n2 - 2, ncp)
            + stats.nct.cdf(-t_critical, n1 + n2 - 2, ncp)
        )

        return max(0.0, min(1.0, power))

    def _generate_recommendation(
        self,
        is_significant: bool,
        practical_significance: bool,
        effect_size: float,
        p_value: float,
        power: float,
    ) -> str:
        """Generate actionable recommendation based on statistical results."""
        if is_significant and practical_significance:
            if effect_size > 0:
                return f"IMPLEMENT: Treatment shows significant improvement (p={p_value:.4f}, effect size={effect_size:.3f})"
            else:
                return f"REJECT: Treatment shows significant degradation (p={p_value:.4f}, effect size={effect_size:.3f})"

        elif is_significant and not practical_significance:
            return f"INCONCLUSIVE: Statistically significant but effect too small (effect size={effect_size:.3f})"

        elif not is_significant and power < 0.8:
            return f"INSUFFICIENT DATA: Low power ({power:.2f}). Collect more data or increase effect size."

        elif not is_significant and power >= 0.8:
            return (
                f"NO EFFECT: Well-powered test shows no significant difference (power={power:.2f})"
            )

        else:
            return f"CONTINUE MONITORING: p={p_value:.4f}, effect size={effect_size:.3f}, power={power:.2f}"

    def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get comprehensive summary of an experiment.

        Args:
            experiment_id: ID of the experiment

        Returns:
            Experiment summary including config, data, and results
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        config = self.experiments[experiment_id]
        data = self.experiment_data[experiment_id]
        results = self.experiment_results[experiment_id]
        status = self.experiment_status[experiment_id]

        # Calculate summary statistics
        variant_counts = defaultdict(int)
        for data_point in data:
            variant_counts[data_point.variant] += 1

        summary = {
            "experiment_id": experiment_id,
            "config": {
                "name": config.name,
                "description": config.description,
                "type": config.experiment_type.value,
                "metric_type": config.metric_type.value,
                "primary_metric": config.primary_metric,
                "significance_level": config.significance_level,
                "power": config.power,
                "min_effect_size": config.min_effect_size,
                "traffic_split": config.traffic_split,
            },
            "status": status.value,
            "data_summary": {
                "total_observations": len(data),
                "variant_counts": dict(variant_counts),
                "start_time": min(d.timestamp for d in data) if data else None,
                "end_time": max(d.timestamp for d in data) if data else None,
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "p_value": r.p_value,
                    "effect_size": r.effect_size,
                    "is_significant": r.is_significant,
                    "practical_significance": r.practical_significance,
                    "recommendation": r.recommendation,
                    "power": r.power,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in results
            ],
        }

        return summary


# Global instance
_ab_testing_framework: Optional[ABTestingFramework] = None


def get_ab_testing_framework() -> ABTestingFramework:
    """Get global A/B testing framework instance."""
    global _ab_testing_framework
    if _ab_testing_framework is None:
        _ab_testing_framework = ABTestingFramework()
    return _ab_testing_framework


def create_ai_model_experiment(
    model_a: str, model_b: str, metric: str = "response_quality", min_effect_size: float = 0.1
) -> str:
    """
    Create an A/B experiment for comparing AI models.

    Args:
        model_a: Name of control model
        model_b: Name of treatment model
        metric: Primary metric to compare
        min_effect_size: Minimum detectable effect size

    Returns:
        Experiment ID
    """
    framework = get_ab_testing_framework()

    config = ExperimentConfig(
        name=f"AI Model Comparison: {model_a} vs {model_b}",
        description=f"Compare performance of {model_a} (control) against {model_b} (treatment)",
        experiment_type=ExperimentType.AI_MODEL_COMPARISON,
        metric_type=MetricType.CONTINUOUS,
        primary_metric=metric,
        secondary_metrics=["response_time", "cost_per_request"],
        min_effect_size=min_effect_size,
        traffic_split={"control": 0.5, "treatment": 0.5},
        min_sample_size=200,
        tags=["ai_model", "performance", model_a, model_b],
    )

    return framework.create_experiment(config)


def create_prompt_optimization_experiment(
    original_prompt: str, optimized_prompt: str, metric: str = "task_completion_rate"
) -> str:
    """
    Create an A/B experiment for prompt optimization.

    Args:
        original_prompt: Original prompt (control)
        optimized_prompt: Optimized prompt (treatment)
        metric: Primary metric to compare

    Returns:
        Experiment ID
    """
    framework = get_ab_testing_framework()

    config = ExperimentConfig(
        name="Prompt Optimization Experiment",
        description="Compare effectiveness of original vs optimized prompt",
        experiment_type=ExperimentType.PROMPT_OPTIMIZATION,
        metric_type=MetricType.BINARY,
        primary_metric=metric,
        secondary_metrics=["user_satisfaction", "response_relevance"],
        min_effect_size=0.05,  # 5% improvement in completion rate
        traffic_split={"control": 0.5, "treatment": 0.5},
        min_sample_size=500,
        tags=["prompt", "optimization", "completion_rate"],
    )

    return framework.create_experiment(config)
