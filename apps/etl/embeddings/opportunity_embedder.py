"""Generate and store embeddings for opportunity search."""

from __future__ import annotations

import logging
from typing import List

from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec

from apps.etl.config import Settings
from apps.etl.models import Opportunity

logger = logging.getLogger(__name__)


class OpportunityEmbedder:
    """Generates embeddings for opportunities and stores in Pinecone."""

    def __init__(self, settings: Settings):
        """Initialize embedder with API clients."""
        self.settings = settings

        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=settings.openai_api_key)

        # Initialize Pinecone client
        if settings.pinecone_api_key:
            self.pinecone_client = Pinecone(api_key=settings.pinecone_api_key)

            # Get or create index
            index_name = settings.pinecone_index
            existing_indexes = [idx.name for idx in self.pinecone_client.list_indexes()]

            if index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {index_name}")
                self.pinecone_client.create_index(
                    name=index_name,
                    dimension=1536,  # text-embedding-ada-002 dimension
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=settings.pinecone_environment
                    )
                )

            self.index = self.pinecone_client.Index(index_name)
            logger.info(f"Connected to Pinecone index: {index_name}")
        else:
            logger.warning("Pinecone API key not configured - skipping vector storage")
            self.index = None

    def create_embedding_text(self, opportunity: Opportunity) -> str:
        """Create rich text representation for embedding."""
        parts = [
            f"Title: {opportunity.title}",
            f"Agency: {opportunity.agency_name}",
        ]

        if opportunity.summary:
            parts.append(f"Summary: {opportunity.summary}")

        if opportunity.description:
            # Truncate description to avoid token limits
            desc = opportunity.description[:1000]
            parts.append(f"Description: {desc}")

        if opportunity.eligibility:
            parts.append(f"Eligibility: {opportunity.eligibility}")

        if opportunity.categories:
            parts.append(f"Categories: {', '.join(opportunity.categories)}")

        return "\n\n".join(parts)

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector using OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def embed_and_store(self, opportunity: Opportunity) -> None:
        """Generate embedding and store in Pinecone."""
        if not self.index:
            logger.debug("Pinecone not configured, skipping embedding storage")
            return

        try:
            # Create embedding text
            text = self.create_embedding_text(opportunity)

            # Generate embedding
            embedding = self.generate_embedding(text)

            # Prepare metadata
            metadata = {
                "opportunity_id": opportunity.opportunity_id,
                "title": opportunity.title,
                "agency": opportunity.agency_name,
                "summary": (opportunity.summary or "")[:1000],  # Truncate for metadata limits
                "deadline": opportunity.close_date.isoformat() if opportunity.close_date else None,
                "award_floor": opportunity.award_floor,
                "award_ceiling": opportunity.award_ceiling,
                "deadline_status": opportunity.deadline_status,
            }

            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(
                    opportunity.opportunity_id,
                    embedding,
                    metadata
                )],
                namespace="opportunities"
            )

            logger.info(f"Stored embedding for opportunity: {opportunity.opportunity_id}")

        except Exception as e:
            logger.error(f"Failed to embed opportunity {opportunity.opportunity_id}: {e}")
            # Don't raise - continue processing other opportunities

    def embed_batch(self, opportunities: List[Opportunity]) -> dict:
        """Embed multiple opportunities in batch."""
        stats = {
            "total": len(opportunities),
            "succeeded": 0,
            "failed": 0,
        }

        for opp in opportunities:
            try:
                self.embed_and_store(opp)
                stats["succeeded"] += 1
            except Exception as e:
                logger.error(f"Failed to process opportunity {opp.opportunity_id}: {e}")
                stats["failed"] += 1

        logger.info(f"Embedding batch complete: {stats}")
        return stats
