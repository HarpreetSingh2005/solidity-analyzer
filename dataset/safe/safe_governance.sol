// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeGovernance {
    mapping(address => uint256) public votes;
    address public governor;

    constructor() {
        governor = msg.sender;
    }

    modifier onlyGovernor() {
        require(msg.sender == governor, "Not governor");
        _;
    }

    function vote(uint256 proposalId) external {
        votes[msg.sender] += 1;
    }

    function executeProposal(uint256 proposalId) external onlyGovernor {
        // governance logic here
    }
}