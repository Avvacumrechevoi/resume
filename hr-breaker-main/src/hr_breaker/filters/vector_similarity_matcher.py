from google import genai
from google.genai import types

from hr_breaker.config import get_settings
from hr_breaker.filters.base import BaseFilter
from hr_breaker.filters.registry import FilterRegistry
from hr_breaker.models import FilterResult, JobPosting, OptimizedResume, ResumeSource


@FilterRegistry.register
class VectorSimilarityMatcher(BaseFilter):
    """Vector similarity filter using Google Gemini embeddings."""

    name = "VectorSimilarityMatcher"
    priority = 6

    @property
    def threshold(self) -> float:
        return get_settings().filter_vector_threshold

    async def evaluate(
        self,
        optimized: OptimizedResume,
        job: JobPosting,
        source: ResumeSource,
    ) -> FilterResult:
        settings = get_settings()

        if optimized.pdf_text is None:
            return FilterResult(
                filter_name=self.name,
                passed=False,
                score=0.0,
                threshold=self.threshold,
                issues=["No PDF text available"],
                suggestions=["Ensure PDF compilation succeeds"],
            )

        client = genai.Client(api_key=settings.google_api_key)

        resume_text = optimized.pdf_text
        job_text = f"{job.title} {job.description} {' '.join(job.requirements)}"

        try:
            result = client.models.embed_content(
                model=settings.embedding_model,
                contents=[resume_text, job_text],
                config=types.EmbedContentConfig(
                    task_type="SEMANTIC_SIMILARITY",
                    output_dimensionality=settings.embedding_output_dimensionality,
                ),
            )
            embeddings = [emb.values for emb in result.embeddings]
        except Exception as e:
            return FilterResult(
                filter_name=self.name,
                passed=True,
                score=1.0,
                threshold=self.threshold,
                issues=[f"Embedding API error: {e}"],
                suggestions=[],
            )

        # Cosine similarity
        e1, e2 = embeddings[0], embeddings[1]
        dot = sum(a * b for a, b in zip(e1, e2))
        norm1 = sum(a * a for a in e1) ** 0.5
        norm2 = sum(b * b for b in e2) ** 0.5
        similarity = dot / (norm1 * norm2) if norm1 and norm2 else 0.0

        # Normalize to 0-1 (cosine similarity is -1 to 1)
        score = (similarity + 1) / 2

        issues = []
        if score < self.threshold:
            issues.append(
                f"Low semantic vector similarity to job posting ({score:.2f})"
            )

        return FilterResult(
            filter_name=self.name,
            passed=score >= self.threshold,
            score=score,
            threshold=self.threshold,
            issues=issues,
            suggestions=[],
        )
