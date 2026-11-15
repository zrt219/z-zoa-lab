// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ResearchNotary
 * @dev Cryptographic run notarization smart contract for Z-ZOA Lab targeting XRPL EVM Sidechain.
 * Enforces sequential stage progression and immutable payload hash anchoring for reproducible astrophysics research.
 */
contract ResearchNotary {
    enum ResearchStage {
        TRAIN_START,          // 0: Initial training run began
        PREDICTION_FROZEN,    // 1: Model predictions sealed & hashed
        HOLDOUT_REVEAL,       // 2: Blinded holdouts unblinded
        VALIDATION_COMPLETE,  // 3: Statistical validation completed
        HYBRID_COMPLETE,      // 4: MeerKAT hybrid reconstruction merged
        PAPER_CANDIDATE       // 5: Final publication bundle sealed
    }

    struct StageRecord {
        string runId;
        ResearchStage stage;
        bytes32 payloadHash;
        bytes32 previousTxOrHash;
        uint256 timestamp;
        address notarizer;
        bool exists;
    }

    // runId => ResearchStage => StageRecord
    mapping(string => mapping(ResearchStage => StageRecord)) private _records;

    // runId => highest anchored stage (-1 if none)
    mapping(string => int8) private _latestStage;

    // Emitted whenever a research stage is anchored
    event ResearchStageAnchored(
        string indexed runId,
        ResearchStage indexed stage,
        bytes32 indexed payloadHash,
        bytes32 previousTxOrHash,
        uint256 timestamp,
        address notarizer
    );

    error InvalidStageProgression(string runId, ResearchStage attempted, int8 currentLatest);
    error StageAlreadyAnchored(string runId, ResearchStage stage, bytes32 existingHash);
    error EmptyRunId();
    error ZeroPayloadHash();

    /**
     * @notice Anchor a research stage payload hash for a given run ID.
     * @param runId Identifier of the research run (e.g., "VELA-001")
     * @param stage The research stage being anchored
     * @param payloadHash SHA-256 (or Keccak256) hash of the canonical anchor manifest
     * @param previousTxOrHash Reference hash of preceding stage or XRPL L1 tx hash
     */
    function anchorStage(
        string calldata runId,
        ResearchStage stage,
        bytes32 payloadHash,
        bytes32 previousTxOrHash
    ) external returns (bool) {
        if (bytes(runId).length == 0) revert EmptyRunId();
        if (payloadHash == bytes32(0)) revert ZeroPayloadHash();

        StageRecord storage existing = _records[runId][stage];
        if (existing.exists) {
            revert StageAlreadyAnchored(runId, stage, existing.payloadHash);
        }

        // Validate sequential chronology:
        // stage 0 (TRAIN_START) or stage must be next in sequence or previous stage must exist
        uint8 stageNum = uint8(stage);
        if (stageNum > 0) {
            ResearchStage prevStage = ResearchStage(stageNum - 1);
            if (!_records[runId][prevStage].exists) {
                revert InvalidStageProgression(runId, stage, getRunLatestStage(runId));
            }
        }

        StageRecord memory newRecord = StageRecord({
            runId: runId,
            stage: stage,
            payloadHash: payloadHash,
            previousTxOrHash: previousTxOrHash,
            timestamp: block.timestamp,
            notarizer: msg.sender,
            exists: true
        });

        _records[runId][stage] = newRecord;

        if (int8(stageNum) > _latestStage[runId]) {
            _latestStage[runId] = int8(stageNum);
        }

        emit ResearchStageAnchored(
            runId,
            stage,
            payloadHash,
            previousTxOrHash,
            block.timestamp,
            msg.sender
        );

        return true;
    }

    /**
     * @notice Retrieve the recorded stage info.
     */
    function getStage(
        string calldata runId,
        ResearchStage stage
    ) external view returns (
        bytes32 payloadHash,
        bytes32 previousTxOrHash,
        uint256 timestamp,
        address notarizer,
        bool exists
    ) {
        StageRecord storage rec = _records[runId][stage];
        return (
            rec.payloadHash,
            rec.previousTxOrHash,
            rec.timestamp,
            rec.notarizer,
            rec.exists
        );
    }

    /**
     * @notice Check if a specific stage has been anchored.
     */
    function isStageAnchored(
        string calldata runId,
        ResearchStage stage
    ) external view returns (bool) {
        return _records[runId][stage].exists;
    }

    /**
     * @notice Verify whether a provided payload hash matches the on-chain notarized hash.
     */
    function verifyPayloadHash(
        string calldata runId,
        ResearchStage stage,
        bytes32 payloadHash
    ) external view returns (bool) {
        StageRecord storage rec = _records[runId][stage];
        if (!rec.exists) {
            return false;
        }
        return rec.payloadHash == payloadHash;
    }

    /**
     * @notice Get latest anchored stage index for a run ID (-1 if none).
     */
    function getRunLatestStage(string calldata runId) public view returns (int8) {
        // If stage 0 hasn't been anchored, check if it exists; if not return -1
        if (!_records[runId][ResearchStage.TRAIN_START].exists) {
            return -1;
        }
        return _latestStage[runId];
    }
}
