// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: tx.origin used for authentication (phishing attack).
contract VulnNewTxOrigin {
    address public owner;
    function withdraw() external {
        require(tx.origin == owner, "Not owner");
        payable(owner).transfer(address(this).balance);
    }
}