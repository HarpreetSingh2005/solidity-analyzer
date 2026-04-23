// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Missing onlyOwner modifier.
contract VulnNewAccessControl {
    address public owner;
    function setOwner(address newOwner) external {
        // Missing access control check
        owner = newOwner;
    }
}