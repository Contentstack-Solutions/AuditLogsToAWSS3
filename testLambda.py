import lambda_function

# stacks = lambda_function.stacks

# for stack in stacks:
#     stack = stack.split(',')
#     res = lambda_function.getAuditLogs('', stack[0], stack[1])
#     print(stack[0])
#     print(stack[1])
#     print(res)

res = lambda_function.lambda_handler('', '') # s3 upload will not work - but others should, with defined env variables.
print(res)