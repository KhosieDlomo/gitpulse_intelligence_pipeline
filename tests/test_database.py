import pytest
import os
from src.database import GitPulseDB

def test_db_operations():
    # Use a separate test database file
    test_db_path = "data/test_gitpulse.db"
    db = GitPulseDB(test_db_path)
    
    sample_data = [{
        'name': 'LogicSolver',
        'stars': 500,
        'label': 'Formal Logic',
        'lang': 'Python',
        'summary': 'A SAT solver for propositional logic.',
        'link': 'http://github.com/logic'
    }]
    
    # Test Save
    db.save_trending(sample_data)
    
    # Test Retrieve Stars
    previous_stars = db.get_previous_stars('LogicSolver')
    assert previous_stars == 500
    
    # Test Non-existent repo
    assert db.get_previous_stars('GhostRepo') is None
    
    # Cleanup
    db.conn.close()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)