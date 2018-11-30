def add_function(func, func_name, func_description, context):
    import dill
    import pandas as pd
    pkl_func = dill.dumps(func)
    new_func = pd.DataFrame([[func_name, pkl_func, func_description, None]],
                          columns=['name', 'function', 'description', 'the_geom'])
    try:
        existing_func = context.read('functions')
    except:
        existing_func = pd.DataFrame(columns=['name', 'function', 'description', 'the_geom'])
    assert not func_name in existing_func.name.values, 'Function Name Duplication Error: Please Rename The Function'
    all_func = existing_func.append(new_func, ignore_index=True, sort=False)
    context.write(all_func , 'functions', overwrite=True)

def delete_function(func_name, context):
    try:
        existing_func = context.read('functions')
        all_func = existing_func[existing_func.name != func_name]
        context.write(all_func , 'functions', overwrite=True)
    except:
        pass

def load_function(func_name, context):
    import dill
    try:
        existing_func = context.read('functions')
        assert func_name in existing_func.name.values, 'Function Not Existed'
        func = eval(existing_func[existing_func.name == func_name]['function'].values[0])
        return dill.loads(func)
    except:
        pass
