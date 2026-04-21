// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Test contract for Dangerous Delegatecall detection
contract DelegatecallUnsafe {
    address public implementation;
    address public owner;

    constructor(address _impl) {
        implementation = _impl;
        owner = msg.sender;
    }

    // VULNERABLE: delegatecall to a mutable state variable
    // Anyone who can change `implementation` can execute arbitrary code
    // in this contract's storage context
    fallback() external payable {
        address impl = implementation;
        assembly {
            // Copy calldata and perform the delegatecall
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(gas(), impl, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result
            case 0 { revert(0, returndatasize()) }
            default { return(0, returndatasize()) }
        }
    }

    // VULNERABLE: allows anyone to change the delegatecall target
    function upgrade(address _newImpl) public {
        // Missing access control — any user can redirect delegatecall
        implementation = _newImpl;
    }

    // VULNERABLE: delegatecall to caller-supplied address
    function executeWith(address _target, bytes calldata _data) public {
        (bool success, ) = _target.delegatecall(_data);
        require(success, "delegatecall failed");
    }
}
