import hashlib
import json
import os
import datetime
import uuid

class EvidenceManager:
    def __init__(self, audit_log_path="evidence_audit_log.json"):
        self.audit_log_path = audit_log_path
        if not os.path.exists(self.audit_log_path):
            with open(self.audit_log_path, 'w') as f:
                json.dump([], f)

    def generate_file_hash(self, file_path):
        """Generates a SHA-256 hash of the file for digital fingerprinting."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def log_evidence(self, file_path, case_id=None):
        """Logs the evidence entry with timestamp and hash."""
        if not case_id:
            case_id = str(uuid.uuid4())
        
        file_hash = self.generate_file_hash(file_path)
        timestamp = datetime.datetime.now().isoformat()
        
        entry = {
            "case_id": case_id,
            "filename": os.path.basename(file_path),
            "file_path": file_path,
            "sha256_hash": file_hash,
            "timestamp": timestamp,
            "status": "ingested"
        }
        
        self._append_to_log(entry)
        return entry

    def log_analysis(self, case_id, file_hash, analysis_results):
        """Logs the results of the analysis linked to the evidence hash."""
        entry = {
            "case_id": case_id,
            "sha256_hash": file_hash,
            "timestamp": datetime.datetime.now().isoformat(),
            "action": "analysis_completed",
            "results_summary": analysis_results
        }
        self._append_to_log(entry)

    def get_history(self):
        """Retrieves the full audit log history."""
        try:
            with open(self.audit_log_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _append_to_log(self, entry):
        """Appends an entry to the JSON audit log."""
        try:
            with open(self.audit_log_path, 'r') as f:
                log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            log = []
        
        log.append(entry)
        
        with open(self.audit_log_path, 'w') as f:
            json.dump(log, f, indent=4)

# Singleton instance
evidence_manager = EvidenceManager()
