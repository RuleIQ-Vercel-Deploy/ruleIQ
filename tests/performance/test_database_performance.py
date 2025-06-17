"""
Database Performance Tests

Tests database query performance, connection handling, and data operations
under various load conditions and data volumes.
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from uuid import uuid4
from typing import List, Dict, Any

from sqlalchemy import text, func
from sqlalchemy.orm import Session


@pytest.mark.performance
@pytest.mark.database
class TestDatabaseQueryPerformance:
    """Test database query performance"""
    
    def test_evidence_query_scaling(self, db_session: Session, sample_user, benchmark):
        """Test how evidence queries scale with data volume"""
        
        # Create large dataset
        evidence_items = []
        for i in range(1000):
            evidence_data = {
                "user_id": sample_user.id,
                "title": f"Scale Test Evidence {i+1:04d}",
                "description": f"Evidence item {i+1} for scaling test",
                "evidence_type": "document",
                "status": ["valid", "expired", "under_review"][i % 3],
                "framework_mappings": [f"ISO27001.A.{i//100 + 1}.{i%10 + 1}"],
                "tags": [f"tag{i%10}", f"category{i%5}"],
                "metadata_": {"test_index": i, "batch": i//100}
            }
            evidence_items.append(evidence_data)
        
        # Bulk insert for faster setup
        from database.evidence_item import EvidenceItem
        evidence_objects = [EvidenceItem(**data) for data in evidence_items]
        db_session.bulk_save_objects(evidence_objects)
        db_session.commit()
        
        def query_evidence_with_filters():
            """Query evidence with complex filters"""
            query = db_session.query(EvidenceItem).filter(
                EvidenceItem.user_id == sample_user.id,
                EvidenceItem.status.in_(["valid", "under_review"]),
                EvidenceItem.title.contains("Evidence")
            ).order_by(EvidenceItem.created_at.desc()).limit(50)
            
            return query.all()
        
        # Benchmark the query
        result = benchmark(query_evidence_with_filters)
        assert len(result) == 50
        
        # Query should remain fast even with 1000 records
        assert benchmark.stats.mean < 0.5  # Mean < 500ms
        assert benchmark.stats.max < 1.0   # Max < 1s
    
    def test_full_text_search_performance(self, db_session: Session, sample_user, benchmark):
        """Test full-text search performance"""
        
        # Create evidence with searchable content
        search_terms = ["security", "policy", "procedure", "compliance", "audit"]
        for i in range(500):
            term = search_terms[i % len(search_terms)]
            evidence_data = {
                "user_id": sample_user.id,
                "title": f"{term.title()} Document {i+1}",
                "description": f"This is a {term} document containing important {term} information and procedures for {term} compliance.",
                "evidence_type": "document",
                "content": f"Detailed {term} content with {term} requirements and {term} procedures." * 10
            }
            
            from database.evidence_item import EvidenceItem
            evidence = EvidenceItem(**evidence_data)
            db_session.add(evidence)
        
        db_session.commit()
        
        def search_evidence():
            """Perform full-text search"""
            search_term = "security compliance"
            query = db_session.query(EvidenceItem).filter(
                EvidenceItem.user_id == sample_user.id,
                EvidenceItem.title.contains(search_term) | 
                EvidenceItem.description.contains(search_term)
            ).limit(20)
            
            return query.all()
        
        result = benchmark(search_evidence)
        assert len(result) > 0
        
        # Full-text search should be reasonably fast
        assert benchmark.stats.mean < 1.0  # Mean < 1s
        assert benchmark.stats.max < 2.0   # Max < 2s
    
    def test_aggregation_query_performance(self, db_session: Session, sample_user, benchmark):
        """Test database aggregation performance"""
        
        # Create diverse evidence data for aggregation
        frameworks = ["GDPR", "ISO27001", "SOC2", "NIST", "PCI_DSS"]
        statuses = ["valid", "expired", "under_review", "draft"]
        types = ["document", "screenshot", "configuration", "audit_log"]
        
        for i in range(200):
            evidence_data = {
                "user_id": sample_user.id,
                "title": f"Aggregation Test Evidence {i+1}",
                "evidence_type": types[i % len(types)],
                "status": statuses[i % len(statuses)],
                "framework_mappings": [f"{frameworks[i % len(frameworks)]}.{i//10}"],
                "quality_score": 60 + (i % 40),  # Scores between 60-99
                "metadata_": {"category": f"cat_{i%5}"}
            }
            
            from database.evidence_item import EvidenceItem
            evidence = EvidenceItem(**evidence_data)
            db_session.add(evidence)
        
        db_session.commit()
        
        def aggregate_evidence_stats():
            """Perform complex aggregation queries"""
            from database.evidence_item import EvidenceItem
            
            # Count by status
            status_counts = db_session.query(
                EvidenceItem.status,
                func.count(EvidenceItem.id)
            ).filter(
                EvidenceItem.user_id == sample_user.id
            ).group_by(EvidenceItem.status).all()
            
            # Count by type
            type_counts = db_session.query(
                EvidenceItem.evidence_type,
                func.count(EvidenceItem.id)
            ).filter(
                EvidenceItem.user_id == sample_user.id
            ).group_by(EvidenceItem.evidence_type).all()
            
            # Average quality score
            avg_quality = db_session.query(
                func.avg(EvidenceItem.quality_score)
            ).filter(
                EvidenceItem.user_id == sample_user.id
            ).scalar()
            
            return {
                "status_counts": dict(status_counts),
                "type_counts": dict(type_counts),
                "avg_quality": float(avg_quality or 0)
            }
        
        result = benchmark(aggregate_evidence_stats)
        assert "status_counts" in result
        assert "type_counts" in result
        assert result["avg_quality"] > 0
        
        # Aggregation should be fast
        assert benchmark.stats.mean < 0.3  # Mean < 300ms
        assert benchmark.stats.max < 1.0   # Max < 1s
    
    def test_join_query_performance(self, db_session: Session, sample_user, benchmark):
        """Test complex join query performance"""
        
        # Create business profile
        from database.business_profile import BusinessProfile
        profile = BusinessProfile(
            user_id=sample_user.id,
            company_name="Join Test Company",
            industry="Technology",
            employee_count=100
        )
        db_session.add(profile)
        db_session.flush()
        
        # Create evidence linked to profile
        from database.evidence_item import EvidenceItem
        for i in range(100):
            evidence = EvidenceItem(
                user_id=sample_user.id,
                business_profile_id=profile.id,
                title=f"Join Test Evidence {i+1}",
                evidence_type="document",
                status="valid"
            )
            db_session.add(evidence)
        
        db_session.commit()
        
        def complex_join_query():
            """Perform complex join query"""
            result = db_session.query(
                EvidenceItem,
                BusinessProfile
            ).join(
                BusinessProfile,
                EvidenceItem.business_profile_id == BusinessProfile.id
            ).filter(
                EvidenceItem.user_id == sample_user.id,
                BusinessProfile.industry == "Technology",
                EvidenceItem.status == "valid"
            ).limit(50).all()
            
            return result
        
        result = benchmark(complex_join_query)
        assert len(result) == 50
        
        # Join queries should be efficient
        assert benchmark.stats.mean < 0.5  # Mean < 500ms
        assert benchmark.stats.max < 1.5   # Max < 1.5s


@pytest.mark.performance
@pytest.mark.database
class TestDatabaseConnectionPerformance:
    """Test database connection handling performance"""
    
    def test_connection_pool_performance(self, db_session: Session):
        """Test connection pool performance under load"""
        
        def database_operation(thread_id: int) -> Dict[str, Any]:
            """Perform database operations in separate thread"""
            start_time = time.time()
            
            try:
                # Simulate typical database operations
                for i in range(10):
                    # Query operation
                    result = db_session.execute(text("SELECT 1 as test_value")).fetchone()
                    assert result.test_value == 1
                    
                    # Insert operation
                    from database.evidence_item import EvidenceItem
                    evidence = EvidenceItem(
                        title=f"Thread {thread_id} Evidence {i+1}",
                        evidence_type="document",
                        user_id=uuid4()  # Random user for test
                    )
                    db_session.add(evidence)
                    db_session.flush()
                    
                    # Update operation
                    evidence.status = "reviewed"
                    db_session.flush()
                
                db_session.commit()
                end_time = time.time()
                
                return {
                    "thread_id": thread_id,
                    "duration": end_time - start_time,
                    "success": True
                }
                
            except Exception as e:
                db_session.rollback()
                return {
                    "thread_id": thread_id,
                    "duration": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                }
        
        # Test with multiple concurrent connections
        num_threads = 20
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(database_operation, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        avg_duration = sum(r["duration"] for r in successful) / len(successful)
        max_duration = max(r["duration"] for r in successful)
        
        # Performance assertions
        assert len(successful) >= num_threads * 0.9  # At least 90% success rate
        assert avg_duration < 2.0  # Average operation < 2s
        assert max_duration < 5.0  # No operation > 5s
        assert len(failed) == 0  # No failed operations
    
    def test_transaction_performance(self, db_session: Session, sample_user, benchmark):
        """Test transaction performance"""
        
        def transaction_operations():
            """Perform multiple operations in single transaction"""
            with db_session.begin():
                # Create multiple related records
                from database.evidence_item import EvidenceItem
                evidence_items = []
                
                for i in range(10):
                    evidence = EvidenceItem(
                        user_id=sample_user.id,
                        title=f"Transaction Test Evidence {i+1}",
                        evidence_type="document",
                        status="valid",
                        metadata_={"batch_id": "transaction_test", "index": i}
                    )
                    db_session.add(evidence)
                    evidence_items.append(evidence)
                
                db_session.flush()
                
                # Update all records
                for evidence in evidence_items:
                    evidence.status = "reviewed"
                    evidence.quality_score = 80 + (evidence_items.index(evidence) % 20)
                
                # Perform aggregation within transaction
                count = db_session.query(EvidenceItem).filter(
                    EvidenceItem.user_id == sample_user.id
                ).count()
                
                return count
        
        result = benchmark(transaction_operations)
        assert result >= 10
        
        # Transactions should be fast
        assert benchmark.stats.mean < 1.0  # Mean < 1s
        assert benchmark.stats.max < 3.0   # Max < 3s
    
    def test_bulk_operation_performance(self, db_session: Session, sample_user, benchmark):
        """Test bulk database operation performance"""
        
        def bulk_insert_operation():
            """Perform bulk insert operation"""
            from database.evidence_item import EvidenceItem
            
            # Prepare bulk data
            evidence_data = []
            for i in range(500):
                evidence_data.append({
                    "user_id": sample_user.id,
                    "title": f"Bulk Evidence {i+1:03d}",
                    "description": f"Bulk inserted evidence item {i+1}",
                    "evidence_type": "document",
                    "status": "valid",
                    "quality_score": 70 + (i % 30),
                    "metadata_": {"bulk_batch": "performance_test", "index": i}
                })
            
            # Bulk insert
            db_session.bulk_insert_mappings(EvidenceItem, evidence_data)
            db_session.commit()
            
            # Verify insertion
            count = db_session.query(EvidenceItem).filter(
                EvidenceItem.user_id == sample_user.id,
                EvidenceItem.title.contains("Bulk Evidence")
            ).count()
            
            return count
        
        result = benchmark(bulk_insert_operation)
        assert result == 500
        
        # Bulk operations should be much faster than individual inserts
        assert benchmark.stats.mean < 2.0  # Mean < 2s for 500 records
        assert benchmark.stats.max < 5.0   # Max < 5s


@pytest.mark.performance
@pytest.mark.database
class TestDatabaseIndexPerformance:
    """Test database index performance"""
    
    def test_indexed_query_performance(self, db_session: Session, sample_user, benchmark):
        """Test performance of queries using database indexes"""
        
        # Create large dataset to test index effectiveness
        from database.evidence_item import EvidenceItem
        for i in range(2000):
            evidence = EvidenceItem(
                user_id=sample_user.id,
                title=f"Index Test Evidence {i+1:04d}",
                evidence_type=["document", "screenshot", "configuration"][i % 3],
                status=["valid", "expired", "under_review"][i % 3],
                framework_mappings=[f"Framework{i//100}.{i%10}"],
                created_at=time.time() - (i * 3600)  # Spread over time
            )
            db_session.add(evidence)
        
        db_session.commit()
        
        def indexed_queries():
            """Perform queries that should use indexes"""
            # Query by user_id (should be indexed)
            user_evidence = db_session.query(EvidenceItem).filter(
                EvidenceItem.user_id == sample_user.id
            ).limit(100).all()
            
            # Query by status (commonly filtered field)
            valid_evidence = db_session.query(EvidenceItem).filter(
                EvidenceItem.user_id == sample_user.id,
                EvidenceItem.status == "valid"
            ).limit(50).all()
            
            # Query by created_at (temporal queries)
            recent_evidence = db_session.query(EvidenceItem).filter(
                EvidenceItem.user_id == sample_user.id,
                EvidenceItem.created_at > time.time() - 86400  # Last 24 hours
            ).order_by(EvidenceItem.created_at.desc()).limit(20).all()
            
            return {
                "user_evidence_count": len(user_evidence),
                "valid_evidence_count": len(valid_evidence),
                "recent_evidence_count": len(recent_evidence)
            }
        
        result = benchmark(indexed_queries)
        assert result["user_evidence_count"] == 100
        assert result["valid_evidence_count"] == 50
        
        # Indexed queries should be very fast even with large dataset
        assert benchmark.stats.mean < 0.2  # Mean < 200ms
        assert benchmark.stats.max < 0.5   # Max < 500ms
    
    def test_unindexed_query_performance(self, db_session: Session, sample_user):
        """Test performance of queries without proper indexes (to identify issues)"""
        
        # Create test data
        from database.evidence_item import EvidenceItem
        for i in range(1000):
            evidence = EvidenceItem(
                user_id=sample_user.id,
                title=f"Unindexed Test Evidence {i+1}",
                description=f"Description with content {i} and metadata",
                evidence_type="document",
                metadata_={"unindexed_field": f"value_{i}", "search_field": f"searchable_{i%100}"}
            )
            db_session.add(evidence)
        
        db_session.commit()
        
        # Query that might not use indexes efficiently
        start_time = time.time()
        
        # Search in text fields (might be unindexed)
        text_search = db_session.query(EvidenceItem).filter(
            EvidenceItem.user_id == sample_user.id,
            EvidenceItem.description.contains("content 500")
        ).all()
        
        text_search_time = time.time() - start_time
        
        # JSON field queries (often unindexed)
        start_time = time.time()
        
        # This query might be slow if JSON fields aren't properly indexed
        json_search = db_session.query(EvidenceItem).filter(
            EvidenceItem.user_id == sample_user.id,
            EvidenceItem.metadata_.contains({"search_field": "searchable_50"})
        ).all()
        
        json_search_time = time.time() - start_time
        
        # Log performance for analysis
        print(f"Text search time: {text_search_time:.3f}s")
        print(f"JSON search time: {json_search_time:.3f}s")
        
        # These queries might be slower, but should still be reasonable
        assert text_search_time < 2.0  # Should be < 2s even without ideal indexing
        assert json_search_time < 3.0  # JSON queries can be slower
        
        assert len(text_search) >= 1
        assert len(json_search) >= 1


@pytest.mark.performance
@pytest.mark.database
class TestDatabaseConcurrencyPerformance:
    """Test database performance under concurrent access"""
    
    def test_concurrent_read_performance(self, db_session: Session, sample_user):
        """Test read performance with concurrent access"""
        
        # Create test data
        from database.evidence_item import EvidenceItem
        for i in range(100):
            evidence = EvidenceItem(
                user_id=sample_user.id,
                title=f"Concurrent Read Test {i+1}",
                evidence_type="document",
                status="valid"
            )
            db_session.add(evidence)
        
        db_session.commit()
        
        def concurrent_read_operation(thread_id: int) -> Dict[str, Any]:
            """Perform read operations concurrently"""
            start_time = time.time()
            
            # Multiple read operations
            operations = [
                # Count query
                lambda: db_session.query(EvidenceItem).filter(
                    EvidenceItem.user_id == sample_user.id
                ).count(),
                
                # List query
                lambda: db_session.query(EvidenceItem).filter(
                    EvidenceItem.user_id == sample_user.id,
                    EvidenceItem.status == "valid"
                ).limit(10).all(),
                
                # Aggregation query
                lambda: db_session.query(
                    func.count(EvidenceItem.id),
                    func.avg(EvidenceItem.quality_score)
                ).filter(
                    EvidenceItem.user_id == sample_user.id
                ).first()
            ]
            
            results = []
            for operation in operations:
                op_start = time.time()
                result = operation()
                op_time = time.time() - op_start
                results.append({"result": result, "time": op_time})
            
            total_time = time.time() - start_time
            
            return {
                "thread_id": thread_id,
                "total_time": total_time,
                "operation_count": len(results),
                "avg_operation_time": sum(r["time"] for r in results) / len(results)
            }
        
        # Run concurrent read operations
        num_threads = 15
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(concurrent_read_operation, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        avg_total_time = sum(r["total_time"] for r in results) / len(results)
        max_total_time = max(r["total_time"] for r in results)
        avg_operation_time = sum(r["avg_operation_time"] for r in results) / len(results)
        
        # Performance assertions for concurrent reads
        assert avg_total_time < 1.0   # Average total time < 1s
        assert max_total_time < 3.0   # Max total time < 3s
        assert avg_operation_time < 0.5  # Average operation time < 500ms
    
    def test_concurrent_write_performance(self, db_session: Session, sample_user):
        """Test write performance with concurrent access"""
        
        def concurrent_write_operation(thread_id: int) -> Dict[str, Any]:
            """Perform write operations concurrently"""
            start_time = time.time()
            
            try:
                # Create evidence items
                from database.evidence_item import EvidenceItem
                evidence_items = []
                
                for i in range(5):
                    evidence = EvidenceItem(
                        user_id=sample_user.id,
                        title=f"Concurrent Write Thread {thread_id} Item {i+1}",
                        evidence_type="document",
                        status="valid",
                        metadata_={"thread_id": thread_id, "item_index": i}
                    )
                    db_session.add(evidence)
                    evidence_items.append(evidence)
                
                db_session.flush()
                
                # Update evidence items
                for evidence in evidence_items:
                    evidence.status = "reviewed"
                    evidence.quality_score = 80 + thread_id
                
                db_session.commit()
                
                end_time = time.time()
                
                return {
                    "thread_id": thread_id,
                    "duration": end_time - start_time,
                    "items_created": len(evidence_items),
                    "success": True
                }
                
            except Exception as e:
                db_session.rollback()
                return {
                    "thread_id": thread_id,
                    "duration": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                }
        
        # Run concurrent write operations
        num_threads = 10
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(concurrent_write_operation, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        avg_duration = sum(r["duration"] for r in successful) / len(successful) if successful else 0
        max_duration = max(r["duration"] for r in successful) if successful else 0
        
        # Performance assertions for concurrent writes
        assert len(successful) >= num_threads * 0.8  # At least 80% success rate
        assert avg_duration < 3.0  # Average write operation < 3s
        assert max_duration < 8.0  # Max write operation < 8s
        
        # Verify data integrity
        from database.evidence_item import EvidenceItem
        total_created = db_session.query(EvidenceItem).filter(
            EvidenceItem.user_id == sample_user.id,
            EvidenceItem.title.contains("Concurrent Write Thread")
        ).count()
        
        expected_items = sum(r["items_created"] for r in successful)
        assert total_created == expected_items  # All successful items should be in database


@pytest.mark.performance
@pytest.mark.database
class TestDatabaseResourceUsage:
    """Test database resource usage and optimization"""
    
    def test_memory_usage_optimization(self, db_session: Session, sample_user):
        """Test memory usage during large result set processing"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large dataset
        from database.evidence_item import EvidenceItem
        for i in range(2000):
            evidence = EvidenceItem(
                user_id=sample_user.id,
                title=f"Memory Test Evidence {i+1:04d}",
                description="x" * 1000,  # 1KB description
                evidence_type="document",
                metadata_={"large_field": "x" * 2000, "index": i}  # 2KB metadata
            )
            db_session.add(evidence)
            
            # Commit in batches to avoid memory issues
            if i % 100 == 99:
                db_session.commit()
        
        db_session.commit()
        
        # Test memory-efficient iteration
        start_time = time.time()
        count = 0
        
        # Use query.yield_per() for memory-efficient iteration
        for evidence in db_session.query(EvidenceItem).filter(
            EvidenceItem.user_id == sample_user.id
        ).yield_per(100):
            count += 1
            # Simulate processing
            _ = len(evidence.title)
        
        iteration_time = time.time() - start_time
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Performance assertions
        assert count == 2000  # All records processed
        assert iteration_time < 10.0  # Should complete in < 10s
        assert memory_increase < 100  # Memory increase should be < 100MB
    
    def test_connection_cleanup(self, db_session: Session):
        """Test that database connections are properly cleaned up"""
        
        # Get initial connection count
        initial_connections = db_session.execute(
            text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
        ).scalar()
        
        def create_temporary_connections():
            """Create and close temporary database connections"""
            from database.db_setup import get_db_session
            
            sessions = []
            for i in range(10):
                session = next(get_db_session())
                sessions.append(session)
                
                # Perform a simple query
                result = session.execute(text("SELECT 1 as test")).scalar()
                assert result == 1
            
            # Close all sessions
            for session in sessions:
                session.close()
        
        # Create and close connections
        create_temporary_connections()
        
        # Allow time for cleanup
        time.sleep(2)
        
        # Check final connection count
        final_connections = db_session.execute(
            text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
        ).scalar()
        
        # Connection count should return to normal (within reasonable variance)
        connection_diff = final_connections - initial_connections
        assert abs(connection_diff) <= 2  # Allow small variance for test connections