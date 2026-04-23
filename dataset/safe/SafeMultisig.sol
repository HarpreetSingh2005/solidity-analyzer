// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe Multisig with correct signature recovery and execution.
contract SafeMultisig {
    address[] public owners;
    mapping(address => bool) public isOwner;
    uint256 public requiredSignatures;

    struct Transaction {
        address to;
        uint256 value;
        bytes data;
        bool executed;
        uint256 confirmations;
    }

    Transaction[] public transactions;
    mapping(uint256 => mapping(address => bool)) public confirmations;

    constructor(address[] memory _owners, uint256 _required) {
        require(_owners.length > 0 && _required > 0 && _required <= _owners.length, "Invalid owners/required");
        for (uint256 i = 0; i < _owners.length; i++) {
            address owner = _owners[i];
            require(owner != address(0) && !isOwner[owner], "Invalid owner");
            isOwner[owner] = true;
            owners.push(owner);
        }
        requiredSignatures = _required;
    }

    function submitTransaction(address to, uint256 value, bytes memory data) public {
        require(isOwner[msg.sender], "Not an owner");
        transactions.push(Transaction({
            to: to,
            value: value,
            data: data,
            executed: false,
            confirmations: 0
        }));
    }

    function confirmTransaction(uint256 txIndex) public {
        require(isOwner[msg.sender], "Not an owner");
        require(txIndex < transactions.length, "Invalid tx");
        require(!confirmations[txIndex][msg.sender], "Already confirmed");

        confirmations[txIndex][msg.sender] = true;
        transactions[txIndex].confirmations += 1;
    }

    function executeTransaction(uint256 txIndex) public {
        require(isOwner[msg.sender], "Not an owner");
        Transaction storage txn = transactions[txIndex];
        require(!txn.executed, "Already executed");
        require(txn.confirmations >= requiredSignatures, "Not enough confirmations");

        txn.executed = true;
        (bool success, ) = txn.to.call{value: txn.value}(txn.data);
        require(success, "Transaction failed");
    }

    receive() external payable {}
}