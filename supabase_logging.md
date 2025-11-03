'''# Supabase Logging for FMCSA Verification

**Version:** 1.0
**Author:** The AI CEO

## 1. Overview

To ensure a complete audit trail and enable powerful data analysis, the results of every FMCSA/DOT verification should be logged to a Supabase database. This creates a persistent, structured record of the verification step for each deal processed by the LendLogic agent.

## 2. Purpose & Benefits

Logging FMCSA data provides several key advantages:

-   **Proof of Verification:** Creates an immutable record that a check was performed, including a timestamp and the exact data found.
-   **Risk Analysis:** Allows for portfolio-wide reporting on carrier risk. You can easily query for all deals involving carriers with "Conditional" safety ratings or those that were "Out of Service."
-   **Historical Tracking:** Enables you to track changes in a carrier's status over time by re-running verifications and comparing the results.

## 3. Supabase Table Schema

It is recommended to add a JSONB column to your main `deals` table in Supabase to store the structured verification data. Alternatively, a separate `fmcsa_verifications` table could be created.

### Option A: JSONB Column in `deals` Table

Add a column named `fmcsa_verification_result` of type `jsonb` to your existing `deals` table.

**SQL to add the column:**
```sql
ALTER TABLE deals
ADD COLUMN fmcsa_verification_result JSONB;
```

### Option B: Dedicated `fmcsa_verifications` Table

For a more normalized structure, create a new table.

**SQL to create the table:**
```sql
CREATE TABLE fmcsa_verifications (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  deal_id BIGINT REFERENCES deals(id) ON DELETE CASCADE,
  dot_number TEXT,
  mc_number TEXT,
  operating_status TEXT,
  safety_rating TEXT,
  fleet_size INT,
  snapshot_url TEXT,
  verification_timestamp TIMESTAMPTZ DEFAULT now(),
  created_at TIMESTAMPTZ DEFAULT now()
);
```

## 4. Data Insertion

When the Manus agent completes the FMCSA lookup, it will format the result as a JSON object. A small server-side function (e.g., a Supabase Edge Function or a backend API endpoint) should be used to take this JSON and insert it into the appropriate table.

### Example JSON Payload

The agent will prepare a JSON object like this, ready for insertion:

```json
{
  "dot_number": "3256789",
  "mc_number": "123456",
  "operating_status": "Active",
  "safety_rating": "Satisfactory",
  "fleet_size": 22,
  "snapshot_url": "https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string=3256789",
  "verification_timestamp": "2025-11-02T23:45:00Z",
  "deal_id": "DEAL-2025-001"
}
```

### Example Insert (JavaScript)

Here is a sample Supabase client-side script to insert the data into the `fmcsa_verifications` table:

```javascript
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'YOUR_SUPABASE_URL';
const supabaseKey = 'YOUR_SUPABASE_ANON_KEY';
const supabase = createClient(supabaseUrl, supabaseKey);

async function logFmcsaResult(fmcsaData) {
  const { data, error } = await supabase
    .from('fmcsa_verifications')
    .insert([fmcsaData]);

  if (error) {
    console.error('Error logging FMCSA data:', error);
    return null;
  }

  console.log('Successfully logged FMCSA verification:', data);
  return data;
}

// Example usage:
const agentOutput = {
  "dot_number": "3256789",
  "mc_number": "123456",
  // ... other fields
  "deal_id": 123 // Assuming deal_id is a number in your DB
};

logFmcsaResult(agentOutput);
```
'''
