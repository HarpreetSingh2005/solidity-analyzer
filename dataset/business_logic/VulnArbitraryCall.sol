// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnArbitraryCall {
    address public owner;
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    // Vulnerability: Arbitrary call execution by anyone
    function execute(address target, bytes memory data) external {
        // Missing onlyOwner modifier!
        (bool success, ) = target.call(data);
        require(success, "Call failed");
    }
}